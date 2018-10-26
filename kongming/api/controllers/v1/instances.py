# Copyright 2018 Huawei Technologies Co.,LTD.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import pecan
from pecan import rest
from six.moves import http_client
import wsme
from wsme import types as wtypes

from oslo_log import log

from kongming.api.controllers import base
from kongming.api.controllers import link
from kongming.api.controllers.v1 import types
from kongming.api.controllers.v1 import utils as api_utils
from kongming.api import expose
from kongming.common import exception
from kongming.common import policy
from kongming.common import clients
from kongming.common import states
from kongming import compute
from kongming import objects


LOG = log.getLogger(__name__)


class Instance(base.APIBase):
    """API representation of a Host.

    This class enforces type checking and value constraints, and converts
    between the internal object model and the API representation of
    an instance.
    """

    uuid = types.uuid
    """The uuid of the instance"""

    status = wtypes.text
    """The status of the instance"""

    cpu_mappings = types.jsontype
    """The CPU mappings of the instance"""

    hosts = wtypes.text
    """The host that the instance is on"""

    mapped_by_kongming = types.boolean
    """Whether this instance has been mapped by kongming or not"""

    links = wsme.wsattr([link.Link], readonly=True)
    """A list containing a self link"""

    def __init__(self, **kwargs):
        self.fields = []
        for field in objects.Instance.fields:
            # Skip fields we do not expose.
            if not hasattr(self, field):
                continue
            self.fields.append(field)
            setattr(self, field, kwargs.get(field, wtypes.Unset))

    @classmethod
    def convert_with_links(cls, obj_instance, mapped_by_kongming=False):
        api_instance = cls(**obj_instance.as_dict())
        api_instance.mapped_by_kongming = mapped_by_kongming
        url = pecan.request.public_url
        api_instance.links = [
            link.Link.make_link(
                'self', url, 'hosts',
                api_instance.uuid),
            link.Link.make_link(
                'bookmark', url, 'hosts',
                api_instance.uuid,
                bookmark=True)
            ]
        return api_instance


class InstanceCollection(base.APIBase):
    """API representation of a collection of Instance."""

    instances = [Instance]
    """A list containing instance objects"""

    @classmethod
    def convert_with_links(cls, obj_instances):
        collection = cls()
        collection.instances = [
            Instance.convert_with_links(obj_instance)
            for obj_instance in obj_instances]
        return collection


class InstancesController(rest.RestController):
    """REST controller for Instance."""

    @policy.authorize_wsgi("kongming:instance", "get")
    @expose.expose(Instance, types.uuid)
    def get_one(self, uuid):
        """Retrieve information about the given instance.

        :param mapping_uuid: UUID of a instance.
        """
        db_host = objects.Instance.get(
            pecan.request.context, uuid)
        try:
            objects.InstanceCPUMapping.get(
                pecan.request.context, uuid)
        except exception.InstanceCPUMappingNotFound:
            mapped_by_kongming = False
        else:
            mapped_by_kongming = True
        return Instance.convert_with_links(db_host, mapped_by_kongming)

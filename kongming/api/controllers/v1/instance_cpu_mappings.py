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
from kongming import objects


LOG = log.getLogger(__name__)


class InstanceCPUMapping(base.APIBase):
    """API representation of a InstanceCPUMapping.

    This class enforces type checking and value constraints, and converts
    between the internal object model and the API representation of
    a mapping.
    """

    instance_uuid = types.uuid
    """The Instance UUID of Instance CPU the mapping that related to"""

    project_id = types.uuid
    """The project UUID of the Instance CPU mapping"""

    user_id = types.uuid
    """The user UUID of the Instance CPU mapping"""

    cpu_mappings = wtypes.text
    """The Instance CPU mapping"""

    host = wtypes.text
    """The host of the instance"""

    links = wsme.wsattr([link.Link], readonly=True)
    """A list containing a self link"""

    def __init__(self, **kwargs):
        self.fields = []
        for field in objects.InstanceCPUMapping.fields:
            # Skip fields we do not expose.
            if not hasattr(self, field):
                continue
            self.fields.append(field)
            setattr(self, field, kwargs.get(field, wtypes.Unset))

    @classmethod
    def convert_with_links(cls, obj_mapping):
        api_mapping = cls(**obj_mapping.as_dict())
        url = pecan.request.public_url
        api_mapping.links = [
            link.Link.make_link(
                'self', url, 'instance_cpu_mappings',
                api_mapping.instance_uuid),
            link.Link.make_link(
                'bookmark', url, 'instance_cpu_mappings',
                api_mapping.instance_uuid,
                bookmark=True)
            ]
        return api_mapping


class InstanceCPUMappingPatchType(types.JsonPatchType):

    _api_base = InstanceCPUMapping

    @staticmethod
    def internal_attrs():
        defaults = types.JsonPatchType.internal_attrs()
        return defaults + ['/project_id', '/user_id', 'instance_uuid']


class InstanceCPUMappingCollection(base.APIBase):
    """API representation of a collection of InstanceCPUMapping."""

    mappings = [InstanceCPUMapping]
    """A list containing mapping objects"""

    @classmethod
    def convert_with_links(cls, obj_mappings):
        collection = cls()
        collection.mappings = [
            InstanceCPUMapping.convert_with_links(obj_mapping)
            for obj_mapping in obj_mappings]
        return collection


class InstanceCPUMapping(rest.RestController):

    _resource = None

    def _get_resource(self, uuid):
        self._resource = objects.InstanceCPUMapping.get(
            pecan.request.context, uuid)
        return self._resource


class InstanceCPUMappingsController(MappingControllerBase):
    """REST controller for InstanceCPUMapping."""

    @policy.authorize_wsgi("kongming:instance_cpu_mapping", "get_one")
    @expose.expose(InstanceCPUMapping, types.uuid)
    def get_one(self, mapping_uuid):
        """Retrieve information about the given mapping.

        :param mapping_uuid: UUID of a mapping.
        """
        db_mapping = objects.InstanceCPUMapping.get(
            pecan.request.context, mapping_uuid)
        if not pecan.request.context.is_admin:
            return InstanceCPUMapping.convert_with_links(
                db_mapping, fields=_DEFAULT_FLAVOR_RETURN_FIELDS)
        else:
            return InstanceCPUMapping.convert_with_links(db_mapping)

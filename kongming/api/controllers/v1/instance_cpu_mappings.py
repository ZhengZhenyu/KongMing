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

    status = wtypes.text
    """The status of the instance cpu mapping"""

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


class InstanceCPUMappingsController(rest.RestController):
    """REST controller for InstanceCPUMapping."""

    @policy.authorize_wsgi("kongming:instance_cpu_mapping", "get")
    @expose.expose(InstanceCPUMapping, types.uuid)
    def get_one(self, instance_uuid):
        """Retrieve information about the given mapping.

        :param mapping_uuid: UUID of a instance.
        """
        db_mapping = objects.InstanceCPUMapping.get(
            pecan.request.context, instance_uuid)
        return InstanceCPUMapping.convert_with_links(db_mapping)

    @policy.authorize_wsgi("kongming:instance_cpu_mapping", "get")
    @expose.expose(InstanceCPUMappingCollection)
    def get_all(self):
        """Retrieve a list of instance_cpu_mappings."""
        mappings = objects.InstanceCPUMapping.list(pecan.request.context)
        return InstanceCPUMappingCollection.convert_with_links(mappings)

    @policy.authorize_wsgi("kongming:instance_cpu_mapping", "create")
    @expose.expose(InstanceCPUMapping, body=types.jsontype,
                   status_code=http_client.CREATED)
    def post(self, mapping):
        """Create a new cpu mapping for the given instance.

        :param mapping: a mapping within the request body.
        :return:
        """
        mapping_dict = {
            'instance_uuid': mapping['instance_uuid'],
            'cpu_mappings': mapping['cpu_mappings'],
            'wait_until_active': False,
            'project_id': pecan.request.context.project_id,
            'user_id': pecan.request.context.user_id
        }

        wait_until_active = mapping.get('wait_until_active')

        mapping = pecan.request.agent_api.create_instance_cpu_mapping(
            pecan.request.context, mapping_dict, wait_until_active)

        pecan.response.location = link.build_url('instance_cpu_mappings',
                                                 mapping.instance_uuid)
        return InstanceCPUMapping.convert_with_links(mapping)

    @policy.authorize_wsgi("kongming:instance_cpu_mapping", "delete")
    @expose.expose(None, types.uuid, status_code=http_client.NO_CONTENT)
    def delete(self, mapping_uuid):
        """Delete a cpu mapping.

        :param mapping_uuid: UUID of a mapping.
        """
        db_mapping = objects.InstanceCPUMapping.get(
            pecan.request.context, mapping_uuid)
        db_mapping.destroy()

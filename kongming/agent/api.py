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

"""Handles all requests relating to compute resources"""

import string

import base64
import binascii

import pecan

from oslo_log import log
from oslo_serialization import base64 as base64utils
from oslo_utils import excutils
from oslo_utils import units
from oslo_utils import uuidutils
import six

from kongming.common import exception
from kongming.common import states
from kongming.common import utils
from kongming.conf import CONF
#from kongming.agent import rpcapi
from kongming import compute
from kongming import objects


LOG = log.getLogger(__name__)


class API(object):
    """API for interacting with the agent manager."""

    def __init__(self, compute_api=None, **kwargs):
        super(API, self).__init__(**kwargs)
        self.compute_api = compute_api or compute.API()
        #self.agent_rpcapi = rpcapi.AgentAPI()

    def _get_instance(self, context, instance_uuid):
        return self.compute_api.get_instance(context, instance_uuid)

    def create_instance_cpu_mapping(self, context, mapping_dict,
                                    wait_until_active):
        if wait_until_active:
            mapping_dict['wait_until_active'] = wait_until_active
        new_mapping = objects.InstanceCPUMapping(context,
                                                 **mapping_dict)
        new_mapping.status = states.PENDING
        # Set the HTTP Location Header

        if not wait_until_active:
            # 1. get instance host from nova api
            inst_dict = self._get_instance(
                context, mapping_dict['instance_uuid'])
            if inst_dict['OS-EXT-STS:vm_state'] != 'active':
                raise exception.BadRequest(
                    reason='Instance should with active vm_state if '
                           'creating cpu mapping without '
                           '"wait_until_active=True".')
            new_mapping.host = inst_dict['OS-EXT-SRV-ATTR:host']

            # 2. call the agent on the instance.host to do the job

        new_mapping.create()

        pecan.request.conductor_api.create_instance_cpu_mapping(
            context, new_mapping)

        return new_mapping

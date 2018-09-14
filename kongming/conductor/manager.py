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

from oslo_log import log as logging
import oslo_messaging as messaging

from kongming.agent import rpcapi as agent_rpcapi
from kongming.common import states
from kongming.conf import CONF


LOG = logging.getLogger(__name__)


class ConductorManager(object):
    """Kongming Conductor manager main class."""

    RPC_API_VERSION = '1.0'
    target = messaging.Target(version=RPC_API_VERSION)

    def __init__(self, topic, host=None):
        super(ConductorManager, self).__init__()
        self.topic = topic
        self.host = host or CONF.host
        self.agent_api = agent_rpcapi.EngineAPI()

    def periodic_tasks(self, context, raise_on_error=False):
        pass

    def create_instance_cpu_mapping(self, context, mapping_obj):
        result = self.agent_api.create_instance_cpu_mapping(
            context, mapping_obj)
        if result:
            mapping_obj.status = states.SUCCEED
            mapping_obj.save()
            LOG.debug('Instance CPU mapping for instance: %s updated '
                      'successfully, set status to %s.',
                      (mapping_obj.instance_uuid, mapping_obj.status))
        else:
            LOG.debug('Instance CPU mapping for instance: %s update '
                      'failed, set status to %s.', mapping_obj.instance_uuid)

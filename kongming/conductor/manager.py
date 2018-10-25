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
from kongming.common import exception
from kongming.common import states
from kongming.conf import CONF
from kongming import objects


LOG = logging.getLogger(__name__)


class ConductorManager(object):
    """Kongming Conductor manager main class."""

    RPC_API_VERSION = '1.0'
    target = messaging.Target(version=RPC_API_VERSION)

    def __init__(self, topic, host=None):
        super(ConductorManager, self).__init__()
        self.topic = topic
        self.host = host or CONF.host
        self.agent_rpcapi = agent_rpcapi.EngineAPI()

    def periodic_tasks(self, context, raise_on_error=False):
        pass

    def update_instance_cpu_mapping(self, context, mapping_obj):
        result = self.agent_rpcapi.update_instance_cpu_mapping(
            context, mapping_obj)
        if result:
            mapping_obj.status = states.SUCCEED
            mapping_obj.save()
            LOG.debug('Instance CPU mapping for instance: %s updated '
                      'successfully, set status to "succeed".',
                      mapping_obj.instance_uuid)
        else:
            LOG.debug('Instance CPU mapping for instance: %s update '
                      'failed.', mapping_obj.instance_uuid)

    def check_and_update_instance_cpu_mapping(self, context,
                                              instance_uuid,
                                              instance_host):
        try:
            db_mapping = objects.InstanceCPUMapping.get(
                context, instance_uuid)
        except exception.InstanceCPUMappingNotFound:
            LOG.debug('Instance CPU mapping for instance: %s not '
                      'exists in the system, do nothing.',
                      instance_uuid)
        else:
            db_mapping.host = instance_host
            result = self.agent_rpcapi.update_instance_cpu_mapping(
                context, db_mapping)
            if result:
                db_mapping.status = states.SUCCEED
                db_mapping.save()
                LOG.debug('Instance CPU mapping for instance: %s updated '
                          'successfully, set status to "succeed".',
                          db_mapping.instance_uuid)
            else:
                LOG.debug('Instance CPU mapping for instance: %s update '
                          'failed.', db_mapping.instance_uuid)

    def check_and_update_host_resources(self, context, host):
        try:
            db_host = objects.Host.get(context, host.host_name)
        except exception.HostNotFound:
            host.create()
        else:
            db_host.cpu_topolody = host.cpu_topology
            db_host.save()
        LOG.debug('Host %s updated successfully.', host.host_name)

    def check_and_update_instances(self, context, host, instances):
        for instance in instances:
            try:
                db_instance = objects.Instance.get(context, instance.uuid)
            except exception.InstanceNotFound:
                instance.create()
            else:
                db_instance.cpu_topolody = instance.cpu_mappings
                db_instance.host = instance.host
                db_instance.status = instance.status
                db_instance.save()
            LOG.debug('Instance %s updated successfully.', instance.uuid)

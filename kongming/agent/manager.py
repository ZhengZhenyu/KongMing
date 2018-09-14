# Copyright 2018 Zhenyu Zheng <zheng.zhenyu@outlook.com>
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

from __future__ import print_function
import libvirt

from oslo_log import log as logging
import oslo_messaging as messaging

from kongming.common import utils
from kongming.conf import CONF

# conn = libvirt.open('qemu:///system')
# hostname = conn.getHostname()
# node_info = conn.getInfo()
# cpu_num = node_info[2]
# numa_nodes_num = node_info[4]
# dom = conn.lookupByUUIDString('827e2a24-7329-4281-b4a2-28f0e0807a51')
# dom_id = dom.ID()
# dom_uuid = dom.UUIDString()
# dom_info = dom.info()  # state, max_mem, mem, cpu_num
# dom.isActive()

LOG = logging.getLogger(__name__)


class AgentManager(object):
    """Kongming Agent manager main class."""

    RPC_API_VERSION = '1.0'
    target = messaging.Target(version=RPC_API_VERSION)

    def __init__(self, topic, host=None):
        self.topic = topic
        self.host = host or CONF.host
        self.conn = libvirt.open('qemu:///system')
        self.hostname = self.conn.getHostname()
        self.maxcpu = self.conn.getInfo()[2]
        LOG.info('The maximum cpu of host %s is %s',
                  self.hostname, self.maxcpu)

    def periodic_tasks(self, context, raise_on_error=False):
        pass

    def execute(self, payload):
        instance_uuid = payload['nova_object.data']['uuid']
        instance_metadata = payload['nova_object.data']['metadata']
        if CONF.agent.agent_trigger_metadata_key in instance_metadata:
            cpu_set_list = instance_metadata[
                CONF.agent.agent_trigger_metadata_key]
            LOG.info('Trying to Pin VCPU for instance %s', instance_uuid)
            pinng_map = utils.calculate_cpumap(cpu_set_list, self.maxcpu)
            LOG.info('The calculated CPU map is ' + str(pinng_map))
            dom = self.conn.lookupByUUIDString(instance_uuid)
            instance_cpu_num = dom.info()[3]
            LOG.info('Pin domain vcpus to host cpu %s.', pinng_map)
            for i in xrange(0, instance_cpu_num):
                LOG.info('Pin domain vcpu %s to host cpu %s with'
                         'flag: %s...' % (i, pinng_map,
                                       libvirt.VIR_DOMAIN_AFFECT_LIVE))
                ret = dom.pinVcpuFlags(i, pinng_map,
                                       libvirt.VIR_DOMAIN_AFFECT_LIVE)
                if ret == 0:
                    LOG.info('...Success')
                else:
                    LOG.info('...Failed')

            LOG.info('VCPU ping for instance %s finished', instance_uuid)

    def adjust_instance_cpu_mapping(self, context, mapping):
        instance_uuid = mapping['instance_uuid']
        cpu_mapping = mapping['cpu_mappings']
        pinng_map = utils.calculate_cpumap(cpu_mapping, self.maxcpu)
        LOG.info('The calculated CPU map is ' + str(pinng_map))
        dom = self.conn.lookupByUUIDString(instance_uuid)
        instance_cpu_num = dom.info()[3]
        LOG.info('Pin domain vcpus to host cpu %s.', pinng_map)
        for i in xrange(0, instance_cpu_num):
            LOG.info('Pin domain vcpu %s to host cpu %s with'
                     'flag: %s...' % (i, pinng_map,
                                      libvirt.VIR_DOMAIN_AFFECT_LIVE))
            ret = dom.pinVcpuFlags(i, pinng_map,
                                   libvirt.VIR_DOMAIN_AFFECT_LIVE)
            if ret == 0:
                LOG.info('...Success')
            else:
                LOG.info('...Failed')

        LOG.info('VCPU ping for instance %s finished', instance_uuid)

        return True

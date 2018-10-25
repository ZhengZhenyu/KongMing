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

import libvirt
from xml.dom import minidom

from oslo_log import log as logging
import oslo_messaging as messaging
from oslo_service import periodic_task

from kongming.common import utils
from kongming.conductor import rpcapi as conductor_rpcapi
from kongming.conf import CONF
from kongming import objects


LOG = logging.getLogger(__name__)


class AgentManager(periodic_task.PeriodicTasks):
    """Kongming Agent manager main class."""

    RPC_API_VERSION = '1.0'
    target = messaging.Target(version=RPC_API_VERSION)

    def __init__(self, topic, host=None):
        super(AgentManager, self).__init__(CONF)
        self.topic = topic
        self.host = host or CONF.host
        self.conn = libvirt.open('qemu:///system')
        self.hostname = self.conn.getHostname()
        self.maxcpu = self.conn.getInfo()[2]
        self.conductor_api = conductor_rpcapi.ConductorAPI()
        self._started = False
        LOG.info('The maximum cpu of host %s is %s',
                  self.hostname, self.maxcpu)

    def init_host(self):
        """Initialize the agent host.

        :param admin_context: the admin context to pass to periodic tasks.
        :raises RuntimeError: when engine is already running.
        """
        if self._started:
            raise RuntimeError(_('Attempt to start an already running '
                                 'engine manager'))

        self._started = True

    def del_host(self):
        self._worker_pool.waitall()
        self._started = False

    def periodic_tasks(self, context, raise_on_error=False):
        return self.run_periodic_tasks(context, raise_on_error=raise_on_error)

    @periodic_task.periodic_task(
        spacing=CONF.agent.update_resources_interval,
        run_immediately=True)
    def _update_resources(self, context):
        """See driver.get_available_resource()

        Periodic process that keeps that the agent's understanding of
        resources in sync with the underlying hypervisor.

        :param context: security context
        """
        self._update_host_resources(context)
        self._update_instances(context)

    def _update_host_resources(self, context):
        host_cpu_topology = {}
        capsXML = self.conn.getCapabilities()

        caps = minidom.parseString(capsXML)
        cells = caps.getElementsByTagName('cells')[0]

        for cell in cells.getElementsByTagName('cell'):
            id = str(cell.getAttribute('id'))
            cpus = cell.getElementsByTagName('cpus')[0]
            cpu_list = [int(cpu.getAttribute('id')) for cpu in
                        cpus.getElementsByTagName('cpu')]
            host_cpu_topology[id] = cpu_list

        host = objects.Host(context, host_name=self.hostname,
                            cpu_topology=host_cpu_topology)

        self.conductor_api.check_and_update_host_resources(
            context, host)

    def _update_instances(self, context, instance_uuid=None):
        instances = []

        if instance_uuid:
            doms = [self.conn.lookupByUUIDString(instance_uuid)]
        else:
            doms = self.conn.listAllDomains(
                libvirt.VIR_CONNECT_LIST_DOMAINS_ACTIVE)

        for dom in doms:
            status, reason = dom.state()
            status = self._map_domain_state(str(status))
            cpu_maps = dom.vcpuPinInfo()
            cpu_map = {}
            cpu_num = 0
            for map in cpu_maps:
                cpu_map[str(cpu_num)] = list(map)
                cpu_num += 1
            instance = objects.Instance(
                context, status=status, uuid=dom.UUIDString(),
                host=self.hostname, cpu_mappings=cpu_map)
            instances.append(instance)

        instance_list_obj = objects.InstanceList(objects=instances)
        self.conductor_api.check_and_update_instances(
            context, self.hostname, instance_list_obj)

    def _map_domain_state(self, status):
        state_dict = {
            "0": "No State",
            "1": "Running",
            "2": "Blocked",
            "3": "Paused",
            "4": "Shutdown",
            "5": "Shutoff",
            "6": "Crashed",
            "7": "Suspended",
            "8": "Last"
        }
        return state_dict[status]

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

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


class ExecutorManager(object):
    """Kongming Executor manager main class."""

    RPC_API_VERSION = '1.0'
    target = messaging.Target(version=RPC_API_VERSION)

    def __init__(self):
        self.conn = libvirt.open('qemu:///system')
        self.hostname = self.conn.getHostname()
        self.maxcpu = self.conn.getInfo()[2]
        LOG.debug('The maximum cpu of host %s is %s',
                  self.hostname, self.maxcpu)

    def execute(self, payload):
        instance_uuid = payload['nova_object.data']['uuid']
        instance_metadata = payload['nova_object.data']['metadata']
        if CONF.executor.executor_trigger_metadata_key in instance_metadata:
            cpu_set_list = instance_metadata[
                CONF.executor.executor_trigger_metadata_key]
            LOG.debug('Trying to Pin VCPU for instance %s', instance_uuid)
            pinng_map = utils.calculate_cpumap(cpu_set_list, self.maxcpu)
            LOG.debug('The calculated CPU map is ' + pinng_map)
            import pdb
            pdb.set_trace()
            dom = self.conn.lookupByUUIDString(instance_uuid)

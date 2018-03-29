from __future__ import print_function
import libvirt

import oslo_messaging as messaging

from kongming.conf import CONF

conn = libvirt.open('qemu:///system')
hostname = conn.getHostname()
node_info = conn.getInfo()
cpu_num = node_info[2]
numa_nodes_num = node_info[4]
dom = conn.lookupByUUIDString('827e2a24-7329-4281-b4a2-28f0e0807a51')
dom_id = dom.ID()
dom_uuid = dom.UUIDString()
dom_info = dom.info()  # state, max_mem, mem, cpu_num
dom.isActive()


class ExecutorManager(object):
    """Kongming Executor manager main class."""

    RPC_API_VERSION = '1.0'
    target = messaging.Target(version=RPC_API_VERSION)

    def __init__(self, topic, host=None):
        super(ExecutorManager, self).__init__()
        self.topic = topic
        self.host = host or CONF.host

    def execute(self, payload):
        pass


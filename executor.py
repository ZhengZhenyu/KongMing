from __future__ import print_function
import sys
import libvirt

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

from __future__ import print_function
import libvirt
import sys
from xml.dom import minidom


conn = libvirt.open('qemu:///system')
capsXML = conn.getCapabilities()

caps = minidom.parseString(capsXML)
cells = caps.getElementsByTagName('cells')[0]

for cell in cells.getElementsByTagName('cell'):
    id = int(cell.getAttribute('id'))
    cpus = cell.getElementsByTagName('cpus')[0]
    cpus = [int(cpu.getAttribute('id')) for cpu in cpus.getElementsByTagName('cpu')]
    print(id)
    print(cpus)

doms = conn.listAllDomains(libvirt.VIR_CONNECT_LIST_DOMAINS_ACTIVE)

for dom in doms:
    cpu_maps = dom.vcpuPinInfo()
    cpu_map = list(cpu_maps[0])
    for raw_cpu_map in cpu_maps:
        for i in xrange(len(cpu_map)):
            cpu_map[i-1] = cpu_map[i-1] or raw_cpu_map[i-1]
    print(dom.UUIDString() + ":")
    print(cpu_map)

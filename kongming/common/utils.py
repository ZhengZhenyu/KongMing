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

import re
import six

from oslo_log import log
from oslo_concurrency import lockutils


def safe_rstrip(value, chars=None):
    """Removes trailing characters from a string if that does not make it empty

    :param value: A string value that will be stripped.
    :param chars: Characters to remove.
    :return: Stripped value.

    """
    if not isinstance(value, six.string_types):
        LOG.warning("Failed to remove trailing character. Returning "
                    "original object. Supplied object is not a string: "
                    "%s,", value)
        return value

    return value.rstrip(chars) or value


def calculate(cpu_set, tpl_map, total):
    """
    Calculate the cpumap for cpu pin.
    :param cpu_set: A string of number(s) divided by '-', '^', or ','
    :param tpl_map: Template cpu map.
    :param total: Total amount of available CPUs.
    :return: A tuple with length of total cpus, with the value of True or
    False indicating the cpu pin policy.
    """
    cpu_map = ()

    try:
        if re.match('\^', cpu_set):
            exclude = int(re.split('\^', cpu_set)[1])
            for i in range(total):
                if i == exclude:
                    cpu_map += (False,)
                else:
                    cpu_map += (tpl_map[i],)

        elif '-' in cpu_set:
            param = re.split('-', cpu_set)
            if not len(param) == 2:
                return False
            if not int(param[1]) < total:
                print("paramlist: out of max range")
                return False
            if int(param[1]) < int(param[0]):
                return False

            for i in range(total):
                if i in range(int(param[0]), int(param[1]) + 1):
                    cpu_map += (True,)
                else:
                    cpu_map += (tpl_map[i],)

        else:
            for i in range(total):
                if i == int(cpu_set):
                    cpu_map += (True,)
                else:
                    cpu_map += (tpl_map[i],)

        return cpu_map
    except ValueError as e:
        print("ValueError: " + str(e))
        return False


def calculate_cpumap(cpu_set_list, total_cpus):
    """
    Calculate the cpumap for cpu pin.
    :param cpu_set_list: A string of numbers divided by '-', '^', and ','
    :param total_cpus: Total amount of available CPUs.
    :return: A tuple with length of total cpus, with the value of True or
    False indicating the cpu pin policy.
    """
    tpl_map = (False,) * total_cpus

    if ',' in cpu_set_list:
        cpu_sets = re.split(',', cpu_set_list)
        for set in cpu_sets:
            cpu_map = calculate(set, tpl_map, total_cpus)
            if cpu_map:
                tpl_map = cpu_map
            else:
                return False
        return cpu_map

    else:
        cpu_map = calculate(cpu_set_list, tpl_map, total_cpus)
    if cpu_map:
        return cpu_map
    else:
        return False


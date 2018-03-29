import re


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
        print "ValueError: " + str(e)
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

# coding=utf-8
# eric_wu<zephor@qq.com>
import os
import platform

import psutil


def ensure_unique(data_path):
    """unique lock for process"""
    try:
        import fcntl
        unique_f = open(os.path.join(data_path, '.unique_'), 'w')
        fcntl.lockf(unique_f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        return False
    return True


def ensure_dir_access(path):
    if not os.path.isdir(path):
        try:
            os.mkdir(path, 0744)
        except:
            return False
    if not os.access(path, os.R_OK | os.W_OK):
        return False
    return True


def get_space(folder, free=True):
    """get free or total space in MB for the folder"""
    if platform.system() == 'Windows':
        import ctypes
        free_bytes = ctypes.c_ulonglong(0)
        total_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(
            ctypes.c_wchar_p(folder),
            ctypes.pointer(free_bytes),
            ctypes.pointer(total_bytes),
            None
        )
        return free_bytes.value / 1024 ** 2 if free else total_bytes.value / 1024 ** 2
    else:
        st = os.statvfs(folder)
        if free:
            return st.f_bavail * st.f_frsize / 1024 ** 2
        else:
            return st.f_blocks * st.f_frsize / 1024 ** 2


def get_ip(inner=True):
    """get ip address"""
    import re
    ip_list = []

    def is_inner_ip(x):
        ip_lst = x.split(".")
        if len(ip_lst) != 4:
            return False
        if ip_lst[0] == "10":
            return True
        if ip_lst[:2] == ["192", "168"]:
            return True
        if ip_lst[0] == "172" and 16 <= int(ip_lst[1]) <= 31:
            return True
        return False

    from netifaces import interfaces, ifaddresses, AF_INET
    for interface in interfaces():
        try:
            links = ifaddresses(interface)[AF_INET]
        except KeyError:
            continue
        for link in links:
            ip_list.append(link['addr'])
    ip_list = filter(lambda x: re.match('^(\d+\.){3}\d+$', x) and x != '127.0.0.1', ip_list)
    inner_list = []
    outer_list = []
    for ip in ip_list:
        if is_inner_ip(ip):
            inner_list.append(ip)
        else:
            outer_list.append(ip)
    if not ip_list:
        raise OSError('pls config the network')
    if inner:
        return inner_list[-1] if inner_list else outer_list[-1]
    elif outer_list:
        return outer_list[-1]
    else:
        raise OSError('no public ip addr found')


def collect_info(root_path):
    """collect system info, storage size will be returned in MB"""
    memory = psutil.virtual_memory()

    info = {
        'hostname': platform.node(),
        'ip': get_ip(inner=True),  # fixme maybe acquire public ip for production
        # fixme this is an unreliable way to calculate total cpu freq
        'cpu_freq': psutil.cpu_freq().current * psutil.cpu_count(),
        'cpu_freq_min': min([freq.min for freq in psutil.cpu_freq(True)]),
        'mem_total': memory.total / 1024 ** 2,
        'storage_total': get_space(root_path,
                                   free=False)
    }
    info.update(collect_running_info(root_path))
    return info


def collect_running_info(root_path):
    memory = psutil.virtual_memory()

    return {
        'mem_available': memory.available / 1024 ** 2 / 10 * 10,
        'mem_free': memory.free / 1024 ** 2,
        'storage_free': get_space(root_path, free=True)
    }


if __name__ == '__main__':
    from configs import cfg

    cfg.bootstrap('dev')

    print collect_info(cfg.sys.data_path)

#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @Date :   2023-03-14
# @Name :   wendr
# `py listen process` request https://www.cnblogs.com/my-python-2019/p/11177224.html

import subprocess
import datetime
import os
import re
from threading import Timer
import time

processinfo = {'name': str, 'pid': int, 'session_name': str, 'session_id': int, 'memory_kb': int}
netstatinfo = {'protocol': str, 'local_addr': str, 'remote_addr': str, 'pid': int}
count = 0
error_count = 0


def get_netstat_info(port: int):
    '''
    获取指定监听端口号的PID进程号
    '''
    read_spec_netstat = subprocess.Popen('netstat -ano | find "0.0.0.0:{_port}"'.format(_port=port), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    try:
        spec_netstat_str = read_spec_netstat.stdout.read().decode(encoding='gbk')
        spec_netstat_array = re.findall(r'([\w\.\*\:]+)', spec_netstat_str)
        # 协议号
        netstatinfo['protocol'] = spec_netstat_array[0]
        # 本地地址:端口
        netstatinfo['local_addr'] = spec_netstat_array[1]
        # 外部地址:端口
        netstatinfo['remote_addr'] = spec_netstat_array[2]
        # PID进程号
        netstatinfo['pid'] = spec_netstat_array[3]
        return netstatinfo
    except Exception:
        return False


def get_tasklist_info(pid: int = None, pro_name: str = None):
    '''
    获取指定PID进程的运行状态, 从tasklist中获取
    获取指定进程名称的运行状态, 从tasklist中获取
    '''
    if pid is None and pro_name is None:
        return None
    elif pid is None:
        read_tasklist = subprocess.Popen('tasklist | find "{_pro_name}"'.format(_pro_name=pro_name), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    else:
        read_tasklist = subprocess.Popen('tasklist | find "{_pid}"'.format(_pid=pid), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    try:
        tasklist_str = read_tasklist.stdout.read().decode(encoding='gbk')
        tasklist_array = re.findall(r'[\w\.\,]+', tasklist_str)
        # 映像名称 , PID
        processinfo['name'] = tasklist_array[0].strip()
        processinfo['pid'] = tasklist_array[1].strip()
        # 会话名 , 会话#
        processinfo['session_name'] = tasklist_array[2].strip()
        processinfo['session_id'] = tasklist_array[3].strip()
        # 内存使用
        processinfo['session_id'] = tasklist_array[4].strip()
        return processinfo
    except Exception:
        return False


def restart_process(process_name):
    '''
    监听指定PID进程, 若进程不存在, 则通过cmd启动该进程
    '''
    formattime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    pid = get_netstat_info(5140)
    global count
    if pid:
        count += 1
        print(formattime + ' : 第' + str(count) + '次检测 正常运行')
    else:
        count += 1
        print(formattime + ' : 第' + str(count) + '次检测 进程不存在')

        cmd = r'cmd.exe /C start C:\Windows\System32\{_process_name}'.format(_process_name=process_name)
        os.system(cmd)
        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ': 正在重启 syslog_udp_server.exe 进程...')
        time.sleep(1)
        reload_pid = get_netstat_info(5140)
        if reload_pid:
            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ': syslog_udp_server.exe 进程启动成功, PID:{_pid}'.format(_pid=reload_pid['pid']))
        else:
            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ': syslog_udp_server.exe 进程启动失败, 正在递归重启进程中...')
            restart_process('syslog_udp_server.exe')
            return
    timer = Timer(20, restart_process, ("syslog_udp_server.exe", ))
    timer.start()
    return


if __name__ == '__main__':
    restart_process('syslog_udp_server.exe')

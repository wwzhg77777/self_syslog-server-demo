#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @Date :   2023-03-14
# @Name :   wendr
# `pysyslogclient` request https://github.com/aboehm/pysyslogclient
# `asyncio` request https://docs.python.org/3/library/asyncio-protocol.html#udp-echo-server
# `requirements.txt` request https://blog.csdn.net/z13653662052/article/details/105602718/
# `nssm install Service` request https://blog.csdn.net/Panda_813/article/details/86686473
# `pywin32 Service`request https://blog.csdn.net/ghostfromheaven/article/details/8604738

import asyncio
import os
import subprocess
import re
from datetime import datetime

processinfo = {'name': str, 'pid': int, 'session_name': str, 'session_id': int, 'memory_kb': int}


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


class EchoServerProtocol:
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode('unicode_escape')  # 将Unicode内存编码值解码成Unicode <=> Ascii
        print(message)
        # remote_addr = ('127.0.0.1', 514)
        # print('Send to %s:%s' % (remote_addr[0], remote_addr[1]))
        # self.transport.sendto(bytes(data), remote_addr)  # 将内容转发给addr对象
        path = r'C:\Program Files (x86)\Syslogd\Logs'
        today = '{_year}-{_month}-{_day}'.format(_year=datetime.now().year, _month=datetime.now().month, _day=str(datetime.now().day).zfill(2))
        logfile = 'Log_010.098.018.009_UDP - {_today}.txt'.format(_today=today)
        with open(os.path.join(path, logfile), 'a+') as file:
            file.write(message)
            file.write('\n')


async def main():
    print("Starting Syslog Listen Server")
    transport, protocol = await loop.create_datagram_endpoint(lambda: EchoServerProtocol(), local_addr=('0.0.0.0', 5140))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        asyncio.ensure_future(main())
        loop.run_forever()
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
        task_pysyslogsrv = get_tasklist_info('PySyslogSrv.exe')
        if task_pysyslogsrv is False:
            os.system('start PySyslogSrv.exe')

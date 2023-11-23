**回顾Windows使用Py 3.8.6 测试Syslog接收，写入。**
案例：Kiwi syslog的UDP接收编码为UTF-8，Client端发来的syslog数据包用的unicode-escape（Unicode内存编码值），导致syslog Server端不能将其解析成utf-8编码，又因Kiwi syslog有其他Client需要走utf-8编码，不能直接修改Kiwi syslog的全局配置（不支持个性化配置）。

因此需要有一个中间件做syslog的代理收发，此案例决定使用Python作为中间件的编写，实际编写耗时为2天半。

**常规syslog处理流程:**
Syslog Client (UTF-8) [Send:udp514]   --->  Kiwi syslog (UTF-8) [Listen:udp514]  -->  LogFile

**Py中间件处理syslog流程:**
Syslog Client (unicode-escape) [Send:udp5140]  --->  Py中间件 (UTF-8) [Listen:udp5140]  --> LogFile

**流程如下：**

1. 创建syslog udp server端代码。用于接收udp协议指定端口的syslog数据包，并提供编码、解码等自定义功能

  ![image-20211109190515573](C:\Users\Administrator\AppData\Roaming\Typora\typora-user-images\image-20211109190515573.png)



2. 使用pysyslogclient 模拟发送syslog包或514端口的udp包，发送给syslog udp server端

  ```bash
  pip install pysyslogclient  # 安装py的syslog client端

  py -m pysyslogclient.cli --server 127.0.0.1 --port 5140 --protocol udp --rfc 3164 --message "Hello World"  # 测试发送syslog包给syslog udp server端
  ```

![image-20211108163945131](C:\Users\Administrator\AppData\Roaming\Typora\typora-user-images\image-20211108163945131.png)



3. 确认本地的模拟收发有效，修改syslog udp server端为Py中间件
       ![image-20211108164007532](C:\Users\Administrator\AppData\Roaming\Typora\typora-user-images\image-20211108164007532.png)



4. 创建PySyslogSrv监听代码，用于监听Py中间件的启动状态，每20秒检测一次，当Py中间件运行错误退出时，PySyslogSrv程序将重启Py中间件。

   ![image-20211109191559040](C:\Users\Administrator\AppData\Roaming\Typora\typora-user-images\image-20211109191559040.png)

   ![image-20211109190832097](C:\Users\Administrator\AppData\Roaming\Typora\typora-user-images\image-20211109190832097.png)



5. `pyinstaller -F` 生成安装包

   ```bash
   pyinstaller -F .\syslog_udp_server.py
   pyinstaller -F .\PySyslogSrv.py
   ```



6. 把syslog_udp_server.exe和PySyslogSrv.exe复制到C:\Windows\System32目录下，CMD运行PySyslogSrv.exe。



7. 修改EDR的发包端口为5410



8. Py中间件接收设备发过来的syslog包，写入到本地记事本，Kiwi Syslog会定期地转移当天日期的日志。

   ![image-20211109191236635](C:\Users\Administrator\AppData\Roaming\Typora\typora-user-images\image-20211109191236635.png)

![image-20211109191304698](C:\Users\Administrator\AppData\Roaming\Typora\typora-user-images\image-20211109191304698.png)



```bash
源代码:
C:\Users\Administrator\Desktop\个人测试用\syslog_send\PySyslogSrv.py
C:\Users\Administrator\Desktop\个人测试用\syslog_send\syslog_udp_server.py
```



参考资料：

 **`pysyslogclient` request https://github.com/aboehm/pysyslogclient**

 **`asyncio` request https://docs.python.org/3/library/asyncio-protocol.html#udp-echo-server**

 **`requirements.txt` request https://blog.csdn.net/z13653662052/article/details/105602718/**

 **`nssm install Service` request https://blog.csdn.net/Panda_813/article/details/86686473**

 **`pywin32 Service`request https://blog.csdn.net/ghostfromheaven/article/details/8604738**

 **`py listen process` request https://www.cnblogs.com/my-python-2019/p/11177224.html**

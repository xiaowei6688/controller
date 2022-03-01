# -*- coding: utf-8 -*-
"""
@File        : serverLink.py
@Author      : Aug
@Time        : 2022/1/10
@Description : 链接服务器 执行命令 上传下载文件

安装 paramiko、func_timeout

pip install paramiko
pip install func_timeout

上传/下载文件 均需要 绝对路径
"""

import paramiko
from func_timeout import func_set_timeout


class LinkServer:
    """
    用户名密码登录 服务器
    """
    def __init__(self, ip, password, userName='root', port=22):
        self.ip = ip
        self.userName = userName
        self.password = password
        self.port = int(port)

    @func_set_timeout(3)
    def ssl_link(self):
        """SSHClient 方式连接
        SSHClient:可以执行命令、关闭
        """
        # 创建SSHClient 实例对象
        ssh = paramiko.SSHClient()
        # 调用方法，表示没有存储远程机器的公钥，允许访问  ；指将目标主机的信息添加至know_hosts文件中
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # 链接远程机器，地址，端口，用户名密码
        ssh.connect(self.ip, self.port, self.userName, self.password)
        self.ssh = ssh

    def transport_link(self):
        """transport 方式链接
        transport：可以执行命令、关闭、上传/下载文件
        :return:
        """
        transport = paramiko.Transport((self.ip, self.port))
        # 建立连接
        transport.connect(username=self.userName, password=self.password)
        # 将sshclient的对象的transport指定为以上的transport
        ssh = paramiko.SSHClient()
        ssh._transport = transport
        self.ssh = ssh

    def invoke_shell_link(self):
        """invoke_shell 方式连接
        """
        # 创建SSHClient 实例对象
        ssh = paramiko.SSHClient()
        # 调用方法，表示没有存储远程机器的公钥，允许访问  ；指将目标主机的信息添加至know_hosts文件中
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # 链接远程机器，地址，端口，用户名密码
        ssh.connect(self.ip, self.port, self.userName, self.password)
        chan = ssh.invoke_shell()
        return chan

    def exec_command(self, command):
        print(f'command：{command}')
        # 执行命令
        stdin, stdout, stderr = self.ssh.exec_command(command)
        # print(f"stdin:{stdin}")
        res = stdout.read() if stdout else stderr.read()
        print(f"result:{res.decode()}")
        return res.decode()

    def upload_files(self, localPath="C:/Users/14418/Desktop/serverLink.py", remotePath="/root/aug-1-11-01/serverLink"
                                                                                        ".py"):
        """
        上传文件 将本地文件上传到远程
        :param localPath: 本地路径
        :param remotePath: 远程路径
        :return:
        """
        sftp = self.ssh.open_sftp()
        sftp.put(localPath, remotePath)
        print('upload_files success')

    def download_file(self, localPath="C:/Users/14418/Desktop/serverLink.py", remotePath="/root/aug-1-11-01"
                                                                                         "/serverLink.py"):
        """
        下载文件 将远程文件下载到本地
        :param localPath: 本地路径
        :param remotePath: 远程路径
        :return:
        """
        sftp = self.ssh.open_sftp()
        sftp.get(remotePath, localPath)
        print('download_file success')

    def close(self):
        # 关闭链接
        self.ssh.close()


if __name__ == '__main__':
    # # 链接服务器1
    # ls = LinkServer(ip='', password='')
    # # 链接服务器2
    # ls_a = LinkServer(ip='', password='')
    #
    # ls.transport_link()  # transport 建立链接
    # ls_a.transport_link()  # transport 建立链接
    #
    # # 创建文件夹
    # cmd = f'mkdir {"aug-1-11-01"}'
    # ls.exec_command(cmd)
    # ls_a.exec_command(cmd)
    #
    # localPath = "C:/Users/14418/Desktop/serverLink.py"
    # remotePath = "/root/aug-1-11-01/serverLink.py"
    # # 上传文件
    # ls.upload_files(localPath, remotePath)
    # ls_a.upload_files(localPath, remotePath)
    #
    # # 下载文件
    # ls.download_file("C:/Users/14418/Desktop/serverLink-zx-01.py", remotePath)
    # ls_a.download_file("C:/Users/14418/Desktop/serverLink-zx-02.py", remotePath)
    #
    # # 关闭链接
    # ls.close()
    # ls_a.close()
    """
    paramiko 连接服务器 使用 docker

    1.直接运行容器       可以
    2.进入容器，执行命令  可以
    3.拉取镜像          不行
    4.删除容器          可以
    5.运行web服务       可以
    """
    # 链接服务器1
    ls = LinkServer(ip='49.232.215.101', password='')
    ls.transport_link()  # transport 建立链接
    # 执行docker命令  # 运行ubuntu 拉取14。04版本
    # ls.exec_command('docker run ubuntu:15.10')
    # ls.exec_command('/bin/echo "Hello world"')
    # ls.exec_command('exit')
    # 删除镜像
    # ls.exec_command('docker rm -f fefb5b3cda85')
    # ls.exec_command('docker run -d -P training/webapp python app.py')
    # 关闭链接
    ls.close()

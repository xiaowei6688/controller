# -*- coding: utf-8 -*-
"""
@File        : one_key.py
@Author      : Aug
@Time        : 2022/2/17
@Description : 一键部署 一键更新 ...

http://121.36.11.194:8000/docs#/

controller
operation-server/
operation-server/requirements.txt
https://github.com/bfl-aug/controller.git
D:\docker-project\test-2\dockerfile
"""
from fastapi import Query
from routers import router as app
from utils import sqlite_db, server_link
import time

app.prefix = '/one_key'
app.tags = ["一键操作"]
server_project_path = "/home/project"
docker_project_path = "/home"

run_command = "python main.py"


def linkedServer(mark):
    """
    链接服务器
    :param mark:服务器标识
    """
    if not mark:
        return False, 'not mark'
    db = sqlite_db.ConnDb()
    sql = f"select * from server where id={mark};"
    query = db.query_sql(sql).fetchone()
    db.db_close()
    if not query:
        return False, {'msg': '服务器不存在'}
    ls = server_link.LinkServer(query[1], query[3], query[2], query[4])
    ls.ssl_link()
    return True, ls


@app.post("/one_click_deployment/")
async def one_click_deployment(
        mark: int = Query(..., description='服务器标识'),
        git_path: str = Query(..., description='git地址'),
        dockerfile_path: str = Query(..., description='dockerfile本地文件路径'),
        requirements_path: str = Query(..., description='requirements文件路径 （项目中文件的路径）'),
        main_path: str = Query(..., description='启动文件目录 （项目中文件的路径）')
):
    """
    一键部署
    -
        :return:
        结果
    """
    status, ls = linkedServer(mark)
    if not status:
        return ls
    try:
        project_name = git_path.split('/')[-1]
        if "." in project_name:
            project_name = project_name.split('.')[0]

        ls.exec_command(f"mkdir {server_project_path}")
        ls.exec_command(f"cd {server_project_path} && git clone {git_path}")
        # 上传文件
        online_df_path = f'{server_project_path}/dockerfile'
        ls.upload_files(dockerfile_path, online_df_path)
        # 创建镜像
        ls.exec_command(f'docker build -t {project_name}:v1 -f {online_df_path} .')
        print('docker build success')

        chan = ls.invoke_shell_link()
        # 生成容器
        chan.send(
            f"docker run -it -p 8000:8000 --name={project_name} -v {server_project_path}/{project_name}:{docker_project_path} {project_name}:v1 /bin/bash \n")
        time.sleep(1)
        chan.send(f'exit \n')
        time.sleep(0.02)
        print((chan.recv(1024 * 1024)).decode())
        chan.close()

        ls.exec_command(f'docker start {project_name}')
        # 安装pip包 operation-server/requirements.txt
        pip_command = f"pip --default-timeout=100 install -r {docker_project_path}/{requirements_path} -i https://pypi.tuna.tsinghua.edu.cn/simple"
        ls.exec_command(f'docker exec {project_name} {pip_command} \n')

        chan1 = ls.invoke_shell_link()
        chan1.send(f'docker exec -it {project_name} /bin/bash \n')
        chan1.send(f"cd {docker_project_path}/{main_path} && {run_command} \n")
        time.sleep(1)
        print((chan1.recv(1024 * 1024)).decode())
        chan1.close()

        ls.close()
        return {
            'msg': 'ok',
            'data': {
                'docker_images_name': project_name + ":v1",
                'docker_name': project_name,
                'project_path': server_project_path,
                'port': '8000'
            }
        }
    except:
        import traceback
        traceback.print_exc()
        return {'msg': 'error'}


@app.post("/git_clone/")
async def git_clone(
        mark: int = Query(..., description='服务器标识'),
        git_path: str = Query(..., description='git 地址'),
):
    """
    git clone
    -
        :return:
        结果
    """
    status, ls = linkedServer(mark)
    if not status:
        return ls
    try:
        ls.exec_command(f"mkdir {server_project_path}")
        ls.exec_command(f"cd {server_project_path} && git clone {git_path}")
        return {'msg': 'ok'}
    except:
        return {'msg': 'error'}


@app.post("/one_click_update/")
async def one_click_update(
        mark: int = Query(..., description='服务器标识'),
        project_name: str = Query(..., description='项目名称'),
        git_path: str = Query(..., description='git 地址'),
        main_path: str = Query(..., description='项目启动地址 （项目中文件的路径）'),
):
    """
    一键更新
    -
        :return:
        结果
    """
    if not project_name:
        return {'msg': 'not project_name'}
    status, ls = linkedServer(mark)
    if not status:
        return ls
    try:
        # ls.exec_command(f'cd {server_project_path} && rm -rf {project_name}/ && git clone {git_path}')
        # ls.exec_command(f'docker restart {project_name}')
        # print('-' * 20)
        # chan = ls.invoke_shell_link()
        # chan.send(f'docker exec -it {project_name} /bin/bash \n')
        # chan.send(f"cd /home/{main_path} && {run_command} \n")
        # time.sleep(1)
        # stdout = chan.recv(1024 * 1024)
        # res = stdout.decode()
        # print(res)
        # if "Application startup complete" in res:
        #     msg = "更新成功"
        # else:
        #     msg = "更新失败，请重试"

        # chan.close()

        # 直接pull更新
        result = ls.exec_command(f'cd {server_project_path}/{project_name} && git pull')
        ls.close()
        return {'msg': result}
    except:
        return {'msg': 'error'}


@app.post("/one_click_start/")
async def one_click_start(
        mark: int = Query(..., description='服务器标识'),
        project_name: str = Query(..., description='项目名称'),
        main_path: str = Query(..., description='项目启动地址 （项目中文件的路径）'),
):
    """
    一键启动
    -
        :return:
        结果
    """
    status, ls = linkedServer(mark)
    if not status:
        return ls
    try:
        res = ls.exec_command(f'docker start {project_name}')
        if project_name not in res:
            return {'msg': 'start error'}

        chan = ls.invoke_shell_link()
        chan.send(f'docker exec -it {project_name} /bin/bash \n')
        chan.send(f"cd /home/{main_path} && {run_command} \n")
        time.sleep(1)
        stdout = chan.recv(1024 * 100)
        res = stdout.decode()
        print(res)
        msg = "成功" if "Application startup complete" in res or "Started reloader process" in res else "失败，请重试"

        chan.close()
        ls.close()
        return {'msg': msg}
    except:
        return {'msg': 'error'}


@app.post("/one_click_stop/")
async def one_click_stop(
        mark: int = Query(..., description='服务器标识'),
        project_name: str = Query(..., description='项目名称')
):
    """
    一键关闭
    -
        :return:
        结果
    """
    status, ls = linkedServer(mark)
    if not status:
        return ls
    try:
        res = ls.exec_command(f"docker stop {project_name}")
        msg = '成功' if project_name in res else "失败，请重试"
        ls.close()
        return {'msg': msg}
    except:
        return {'msg': 'error'}


@app.post("/one_click_reboot/")
async def one_click_reboot(
        mark: int = Query(..., description='服务器标识'),
        project_name: str = Query(..., description='项目名称'),
        main_path: str = Query(..., description='项目启动地址 （项目中文件的路径）'),
):
    """
    一键重启
    -
        :return:
        结果
    """
    status, ls = linkedServer(mark)
    if not status:
        return ls
    try:
        res = ls.exec_command(f'docker restart {project_name}')
        if project_name not in res:
            return {'msg': 'start error'}

        chan = ls.invoke_shell_link()
        chan.send(f'docker exec -it {project_name} /bin/bash \n')
        chan.send(f"cd /home/{main_path} && {run_command} \n")
        time.sleep(1)
        stdout = chan.recv(1024 * 100)
        res = stdout.decode()
        print(res)
        msg = "成功" if "Application startup complete" in res or "Started reloader process" in res else "失败，请重试"

        chan.close()
        ls.close()
        return {'msg': msg}
    except:
        return {'msg': 'error'}


@app.get("/git_install")
def git_install(
        mark: str = Query(..., description='服务器标识'),
        git_name: str = Query(..., description='git name'),
        git_email: str = Query(..., description='git email')
):
    """
    git 安装
    -
        :return:
    """
    status, ls = linkedServer(mark)
    if not status:
        return ls
    try:
        # 安装git
        ls.exec_command("sudo yum install -y git")
        ls.exec_command(f"git config --global user.name '{git_name}'")
        ls.exec_command(f"git config --global user.email '{git_email}'")
        # 生成rsa
        chan = ls.invoke_shell_link()
        com_create_rsa_file = f"ssh-keygen -t rsa -C '{git_email}' \n"
        chan.send(com_create_rsa_file)
        time.sleep(0.3)
        for i in range(3):
            chan.send('\n')
            time.sleep(0.2)
        stdout = chan.recv(1024)
        res = stdout.decode()
        print(res)
        ls.ssl_link()
        # 获取rsa key
        pub_path = "/root/.ssh/id_rsa.pub"
        find_result = ls.exec_command(f"cat {pub_path}")
        ls.close()
        # find_result = find_result.split('\n')
        return {'msg': 'ok', 'data': find_result}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'msg': 'error'}

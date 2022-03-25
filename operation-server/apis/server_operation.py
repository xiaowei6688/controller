# -*- coding: utf-8 -*-
"""
@File        : server_operation.py
@Author      : Aug
@Time        : 2022/2/8
@Description : 对服务器操作
"""
from fastapi import Query
from utils import sqlite_db, server_link
from func_timeout import exceptions
from config import saveRoute
from typing import List, Optional
from utils.log_setting import log_error
from pydantic import BaseModel
from routers import router as app

app.prefix = '/api'
app.tags = ["对服务器操作"]


class Params_create_link(BaseModel):
    """参数校验"""
    ip: str = Query(..., description='服务器ip')
    username: str = Query('root', description='账户')
    password: str = Query(..., description='密码')
    port: Optional[str] = Query("22", description='端口')

    class Config:
        schema_extra = {
            "example": {
                "ip": "10.1.1.1 | 服务器ip",
                "username": "root | 账户",
                "password": "123123 | 密码",
                "port": "22 | 端口"
            }
        }


@app.post("/create_link/")
def create_link(params: Params_create_link):
    """创建服务器链接
    -
    :param params:
    -
        :return:
            返回服务器信息标识
            result:结果描述
            mark:服务器标识
    """
    try:
        ls = server_link.LinkServer(params.ip, params.password, params.username, params.port)
        ls.ssl_link()
    except exceptions.FunctionTimedOut:
        return {'msg': '服务器连接超时'}
    except Exception as e:
        return {'msg': 'ip/账户/密码 错误'}

    params = dict(params)
    db = sqlite_db.ConnDb()
    query = db.get_server_id(params).fetchone()
    if query:
        return {'msg': 'ok', 'mark': query[0]}
    db.create_server(params)
    query = db.get_server_id(params).fetchone()[0]
    db.db_close()
    return {'msg': 'ok', 'mark': query}


@app.get("/get_server/")
async def get_server():
    """
    获取所有服务器
    -
        :return:服务器列表
    """
    db = sqlite_db.ConnDb()
    sql = "select * from server"
    result = db.query_sql(sql).fetchall()
    db.db_close()
    return {'msg': 'ok', 'data': result}


@app.post("/delete_server")
async def delete_server(mark: int = Query(..., description='服务器标识')):
    """
    删除服务器
    -
        :return:
    """
    db = sqlite_db.ConnDb()
    sql = f"delete from server where id={mark};"
    db.execute_sql(sql)
    db.db_close()
    return {'msg': 'ok'}


@app.get("/file_path")
async def get_file_path(
        file_name: str = Query(..., description='查询的文件名'),
        marks: str = Query(..., description='服务器标识 可以传多个 ‘,’隔开'),
        types: str = Query('0', description='查找类型 (0模糊查询1绝对查询)')
):
    """
    获取文件路径
    -
        :return:
        data [
            {"mark": “服务器标识”, "find_result": [目标路径]},
            {"mark": “服务器标识”, "find_result": [目标路径]}
            ...
        ]
    """
    marks = marks.split(',')
    result = []
    for i in marks:
        try:
            if not i:
                continue
            db = sqlite_db.ConnDb()
            sql = f"select * from server where id={int(i)};"
            query = db.query_sql(sql).fetchone()
            db.db_close()
            if not query:
                continue
            ls = server_link.LinkServer(query[1], query[3], query[2], query[4])
            ls.ssl_link()
            if types == '1':
                command = f'find / -iname {file_name}'
            else:
                command = f'find / -iname "*{file_name}*"'
            find_result = ls.exec_command(command)
            ls.close()
            find_result = find_result.split('\n')[:-1]
            result.append({
                "mark": i,
                "find_result": find_result
            })
        except:
            continue
    return {'msg': 'ok', 'data': result}


@app.get("/cat_file")
def cat_file(
        file_path: str = Query(..., description='文件路径 示例：/root/aug/123test.txt'),
        mark: str = Query(..., description='服务器标识')
):
    """
    查看文件
    -
        :return:
        data文件内容
    """
    try:
        if not mark:
            return 'not mark'
        db = sqlite_db.ConnDb()
        sql = f"select * from server where id={int(mark)};"
        query = db.query_sql(sql).fetchone()
        db.db_close()
        if not query:
            return 'mark error'
        ls = server_link.LinkServer(query[1], query[3], query[2], query[4])
        ls.ssl_link()
        find_result = ls.exec_command(f'cat {file_path}')
        ls.close()
        find_result = find_result.split('\n')
        return {'msg': 'ok', 'data': find_result}
    except Exception as e:
        log_error(e)
        return {'msg': 'error'}


@app.get("/download_file/")
def download_file(
        file_name: str = Query(..., description='文件名称'),
        remotePath: str = Query(..., description='文件远程路径 结尾带 "\/"or "/" '),
        fileSavePath: str = Query('', description='文件保存路径(带文件名称) 默认路径为当前项目下 files/文件名'),
        mark: int = Query(..., description='服务器标识')
):
    """
    下载文件
    -
        :return:
        data:文件保存路径
    """
    db = sqlite_db.ConnDb()
    sql = f"select * from server where id={mark};"
    query = db.query_sql(sql).fetchone()
    db.db_close()
    if not query:
        return {'msg': '服务器不存在'}
    if not fileSavePath:
        fileSavePath = saveRoute + file_name
    ls = server_link.LinkServer(query[1], query[3], query[2], query[4])
    ls.transport_link()
    ls.download_file(fileSavePath, remotePath + file_name)
    ls.close()
    return {'msg': 'ok', 'data': fileSavePath}


@app.post("/upload_file")
def upload_file(
        # file: UploadFile = File(...),
        file_path: str = Query(..., description="上传文件本地路径"),
        remote_list: List[dict] = [{"remotePath": '文件件远程存储路径 结尾带 "\/"or "/" ', "mark": '服务器标识'}]
):
    """
    上传文件至服务器
    -
        :return:
        success成功的
        failure失败的
    """
    success_list = []
    failure_list = []
    for i in remote_list:
        mark = i.get('mark')
        if not mark:
            failure_list.append({"data": i, "reason": "not mark"})
            continue
        remote_path = i.get('remotePath')
        if not remote_path:
            failure_list.append({"data": i, "reason": "not remote_path"})
            continue
        db = sqlite_db.ConnDb()
        sql = f"select * from server where id={int(mark)};"
        query = db.query_sql(sql).fetchone()
        db.db_close()
        if not query:
            failure_list.append({"data": i, "reason": "服务器不存在"})
            continue
        ls = server_link.LinkServer(query[1], query[3], query[2], query[4])
        ls.transport_link()
        # ls.upload_files(saveRoute + file_path, remote_path + file_path)
        ls.upload_files(file_path, "/home/project/dockerfile")
        ls.close()
        success_list.append({"data": i})
    return {'msg': 'ok', 'data': {
        "success": success_list,
        "failure": failure_list
    }}


@app.get("/excuting_an_order")
def excuting_an_order(
        command: str = Query(..., description='命令 示例：ll'),
        marks: str = Query(..., description='服务器标识  可以传多个 ‘,’隔开')
):
    """
    多服务器/单服务器 运行 相同命令
    -
        :return:
        success成功的
        failure失败的
    """
    try:
        marks = marks.split(',')
        success_list = []
        failure_list = []
        for mark in marks:
            if not mark:
                failure_list.append({'mark': mark, 'msg': 'not mark'})
                continue
            db = sqlite_db.ConnDb()
            sql = f"select * from server where id={int(mark)};"
            query = db.query_sql(sql).fetchone()
            db.db_close()
            if not query:
                failure_list.append({'mark': mark, 'msg': 'mark error'})
                continue
            ls = server_link.LinkServer(query[1], query[3], query[2], query[4])
            ls.ssl_link()
            find_result = ls.exec_command(command)
            ls.close()
            find_result = find_result.split('\n')
            success_list.append({
                'mark': mark,
                'result': list(filter(None, find_result))
            })
        return {'msg': 'ok', 'data': {
            "success": success_list,
            "failure": failure_list
        }}
    except Exception as e:
        log_error(e)
        return {'msg': 'error'}


@app.post("/excuting_an_order_two")
async def excuting_an_order_two(
        remote_list: List[dict] = [{"command": '命令', "mark": '服务器标识'}]
):
    """
    多服务器/单服务器 运行 不同命令
    -
        :return:
        success成功的
        failure失败的
    """
    try:
        success_list = []
        failure_list = []
        for i in remote_list:
            mark = i.get('mark')
            if not mark:
                failure_list.append({'mark': mark, 'msg': 'not mark'})
                continue
            command = i.get('command')
            if not command:
                failure_list.append({'mark': mark, 'msg': 'not command'})
                continue
            db = sqlite_db.ConnDb()
            sql = f"select * from server where id={int(mark)};"
            query = db.query_sql(sql).fetchone()
            db.db_close()
            if not query:
                failure_list.append({'mark': mark, 'msg': 'mark error'})
                continue
            ls = server_link.LinkServer(query[1], query[3], query[2], query[4])
            ls.ssl_link()
            find_result = ls.exec_command(command)
            ls.close()
            find_result = find_result.split('\n')
            success_list.append({
                'mark': mark,
                'result': list(filter(None, find_result))
            })
        return {'msg': 'ok', 'data': {
            "success": success_list,
            "failure": failure_list
        }}
    except Exception as e:
        log_error(e)
        return {'msg': 'error'}


@app.get("/delete_file")
def delete_file(
        file_path: str = Query(..., description='文件路径名称 示例: /root/aug/123.txt'),
        mark: str = Query(..., description='服务器标识')
):
    """
    删除文件
    -
        :return:
    """
    try:
        if not mark:
            return {'mark': mark, 'msg': 'not mark'}
        if not file_path:
            return {'mark': mark, 'msg': 'not file_path'}
        commands = ['-rf', '-f']
        for c in commands:
            if c in file_path:
                return {'mark': mark, 'msg': 'file_path 包含敏感字符'}
        if '/*' == file_path or '/' == file_path or '*' == file_path:
            return {'mark': mark, 'msg': 'file_path 包含敏感字符'}
        if '.' not in file_path:
            return {'mark': mark, 'msg': '仅支持删除带文件后缀的文件'}
        db = sqlite_db.ConnDb()
        sql = f"select * from server where id={int(mark)};"
        query = db.query_sql(sql).fetchone()
        db.db_close()
        if not query:
            return {'mark': mark, 'msg': 'mark error'}
        ls = server_link.LinkServer(query[1], query[3], query[2], query[4])
        ls.ssl_link()
        find_result = ls.exec_command('rm -f '+file_path)
        ls.close()

        return {'msg': 'ok'}
    except Exception as e:
        log_error(e)
        return {'msg': 'error'}

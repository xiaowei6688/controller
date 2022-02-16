# -*- coding: utf-8 -*-
"""
@File        : req_params.py
@Author      : Aug
@Time        : 2022/2/8
@Description : 参数校验
"""
from typing import Optional

from fastapi import Query, Body
from pydantic import BaseModel


class Params_create_link(BaseModel):
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

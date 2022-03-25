# -*- coding: utf-8 -*-
"""
@File        : main.py
@Author      : Aug
@Time        : 2022/2/8
@Description :
"""
import uvicorn
from fastapi import FastAPI, Request
import time
from utils import log_setting
import routers

# # 初始化数据库 只需要执行一次
# from utils import sqlite_db
# sqlite_db.ConnDb().init_table()


tags_metadata = [
    {
        'name': '',
        'description': 'Operations with api',
    }
]

app = FastAPI(
    title='远程操作服务器',
    version='0.0.2',
    openapi_tags=tags_metadata,
    # docs_url=None,
    # redoc_url=None
)

app.include_router(
    routers.router,
    prefix=''
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    request_content = f"request: ip:{request.client.host}; url:{request.url}; params:[{request.query_params}];"
    log_setting.log_record(request_content)

    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

if __name__ == '__main__':
    uvicorn.run(app='main:app', host="0.0.0.0", port=8000, reload=True, debug=True)


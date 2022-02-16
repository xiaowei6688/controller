# -*- coding: utf-8 -*-
"""
@File        : main.py
@Author      : Aug
@Time        : 2022/2/8
@Description :
"""
import uvicorn
from fastapi import FastAPI, Request
from apis import view
import time
import log_setting

# 初始化数据库 只需要执行一次
# from utils import sqlite_db
# db = sqlite_db.ConnDb().init_table()


tags_metadata = [
    {
        'name': 'api',
        'description': 'Operations with api',
    }
]

app = FastAPI(
    title='操作服务器',
    version='0.0.1',
    openapi_tags=tags_metadata,
    # docs_url=None,
    # redoc_url=None
)

app.include_router(
    view.app,
    prefix=''
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    request_content = f"request: url:{request.client.host}; url:{request.url}; params:[{request.query_params}];"
    log_setting.log_record(request_content)

    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

if __name__ == '__main__':
    uvicorn.run(app='main:app', host="127.0.0.1", port=8000, reload=True, debug=True)

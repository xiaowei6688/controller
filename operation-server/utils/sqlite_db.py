# -*- coding: utf-8 -*-
"""
@File        : sqlite_db.py
@Author      : Aug
@Time        : 2022/2/8
@Description : sqlite数据库操作
"""
import sqlite3


class ConnDb(object):
    """链接数据库
    """
    def __init__(self):
        self.conn = sqlite3.connect('./db/server.db')  # 存在就连接，不存在就创建数据库
        self.c = self.conn.cursor()  # 创建游标

    def query_sql(self, sql):
        """
        执行select并返回数据的方法
        :param sql:
        :return:
        """
        result = self.c.execute(sql)
        self.conn.commit()
        return result

    def execute_sql(self, sql):
        """
        执行除select外的语句
        :param sql:
        :return:
        """
        result = self.c.execute(sql)
        # print("the result is:", result)
        # if "create table" in str(sql).lower():
        #     print("Table created successfully")
        # else:
        #     print("the createdb.sql execute is successfully")
        self.conn.commit()

    def db_close(self):
        """
        断开连接
        :return:
        """
        self.c.close()
        self.conn.close()

    def init_table(self):
        """
        初始化server表
        :return:
        """
        # 服务器
        self.execute_sql("""
        create TABLE IF NOT EXISTS server(
         id  INTEGER   PRIMARY KEY AUTOINCREMENT,
            `ip` varchar(255) DEFAULT NULL,
            `name` varchar(255) DEFAULT NULL,
            `pwd` varchar(255) DEFAULT NULL,
            `port` varchar(255) DEFAULT NULL
        );""")
        self.db_close()

    def create_server(self, data):
        """
        创建服务器
        :return:
        """
        insert_sql = """
        INSERT INTO server 
            (`ip`,`name`,`pwd`,`port`)
        VALUES ('%s','%s','%s','%s')
        """ % (data.get('ip'), data.get('username'), data.get('password'), data.get('port'))
        self.execute_sql(insert_sql)
        return True

    def get_server_id(self, data):
        """
        获取当前服务器信息
        :param data:
        :return:
        """
        query_sql = f"select id from server where `ip`='{data.get('ip')}' and `name`='{data.get('username')}' and `pwd`='{data.get('password')}' and `port`='{data.get('port')}'"
        return self.query_sql(query_sql)


if __name__ == "__main__":
    db = ConnDb()
    # sql = "select qq_number from table0607 where id>4366"
    db.create_server({'ip': '127.0.0.1', 'name': 'root', 'pwd': '123123', 'host': '22'})

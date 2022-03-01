import logging
import os
import traceback
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler


def log_packaging(log_name, file_path, level, logsavetype="time"):
    # 创建日志收集器
    logger_ = logging.getLogger(name=log_name)
    # 日志级别：收集器、渠道,可以不同的渠道输出日志级别不一样
    logger_.setLevel(level)
    # 创建日志收集渠道
    # 1.控制台渠道
    cmd = logging.StreamHandler()
    # 2.文件渠道
    log_path = r"{}/logs/".format(os.getcwd())
    # log_name = log_path + 'error/logging_error.log'
    logfile = log_path + file_path
    # 校验文件是否存在 不存在则创建
    if not os.path.isfile(logfile):
        os.makedirs(log_path + file_path.split('/')[0])
        open(logfile, 'w').close()
    if logsavetype == "time":
        # 根据时间保存日志 一天一个、上限15
        fh = TimedRotatingFileHandler(
            filename=logfile, when="D", encoding='utf-8', interval=1, backupCount=15)
    elif logsavetype == "file_size":
        # 已文件大小保存 1024kb一个、上限15
        fh = RotatingFileHandler(
            filename=logfile, maxBytes=1024, encoding='utf-8', backupCount=15)
    else:
        fh = TimedRotatingFileHandler(
            filename=logfile, when="D", encoding='utf-8', interval=1, backupCount=15)
    fh.suffix = "%Y-%m-%d.log"
    fh.setLevel(level)  # 输出到file的log等级的开关

    # 日志格式
    fmt = '%(asctime)s-%(name)s-%(levelname)s-%(filename)s-%(funcName)s-[line:%(lineno)d]：%(message)s'
    formatter = logging.Formatter(fmt=fmt)

    # 渠道添加格式
    # cmd.setFormatter(formatter)
    fh.setFormatter(formatter)

    # 收集器输出渠道添加
    logger_.addHandler(cmd)
    logger_.addHandler(fh)

    return logger_


# [log error]
log_error = log_packaging("log_error", "error/logging_error.log", logging.ERROR, 'file_size').error

# [log info]
# log_info = log_packaging("log_info", "info/logging_info.log", logging.INFO, 'file_size').info

# [log debug]
# log_debug = log_packaging("log_debug","error/logging_debug.log",logging.DEBUG).info

# [log record info]
log_record = log_packaging("log_record", "record/logging_record.log", logging.INFO).info


if __name__ == "__main__":
    log_record('info')
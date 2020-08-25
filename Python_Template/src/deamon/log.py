import sys
import logging  # 引入logging模块
import os.path
import time
# 第一步，创建一个logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Log等级总开关
# 第二步，创建一个handler，用于写入日志文件
rq = time.strftime('%Y%m%d', time.localtime(time.time()))
log_path = sys.path[0]
log_path = log_path[0:log_path.rfind('/src')] + '/log/'
logfile = log_path + rq + '.log'

if not os.path.exists(log_path):
    os.makedirs(log_path)

fh = logging.FileHandler(logfile, mode='a+')  # 将内容写入日志

fh.setLevel(logging.DEBUG)  # 输出到file的log等级的开关
# 第三步，定义handler的输出格式
formatter = logging.Formatter(
    "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)
# 第四步，将logger添加到handler里面
logger.addHandler(fh)
# # 日志
# logger.debug('this is a logger debug message')
# logger.info('this is a logger info message')
# logger.warning('this is a logger warning message')
# logger.error('this is a logger error message')
# logger.critical('this is a logger critical message')
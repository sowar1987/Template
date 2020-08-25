import sys
import configparser


class Config:
    def __init__(self, funcN):
        if funcN == 'mysql':
            self.mysql_path = sys.path[0]
            self.mysql_path = self.mysql_path[
                0:self.mysql_path.rfind('/src')] + '/config/mysql.ini'
        elif funcN == 'target':
            self.target_path = sys.path[0]
            self.target_path = self.target_path[
                0:self.target_path.rfind('/src')] + '/config/target.ini'
        else:
            print('解析参数错误')

    def get_config(self, config_path):
        """获取指定文件对象"""
        config = configparser.ConfigParser()
        config.read(config_path, encoding="utf-8")
        return config

    def get_mysqldata(self):
        """"获取数据库配置信息"""
        config = self.get_config(self.mysql_path)
        return dict(config.items("mysql"))

    def get_targetdata(self):
        """"获取目标网站配置信息"""
        config = self.get_config(self.target_path)
        # return dict(config.items("target1"))
        return dict(config)
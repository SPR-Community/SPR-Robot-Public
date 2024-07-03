import yaml
import os
import time
import re


class Config:
    def __init__(self, filepath='./config.yml'):
        self.filepath = filepath
        self.config = {}  # 初始化 self.config 为空字典
        if not os.path.exists(filepath):
            self.default_set()
        self.load_config()

    def load_config(self):
        try:
            with open(self.filepath, 'r', encoding='utf-8') as file:
                config = yaml.load(file, Loader=yaml.FullLoader)
        except FileNotFoundError:
            raise FileNotFoundError("Config file not found.")
        
        self.version = config.get('version', '3.0.0 alpha-4')
        self.url = config.get('ws-url', 'ws://127.0.0.1')
        self.loglevel = config.get('log-level', 'INFO') if config.get('log-level') in ['INFO', 'DEBUG'] else 'INFO'
        self.logdir = config.get('log-save', './logs')
        self.plugdir = config.get('plugins-dir', './plugins')
        self.retry = config.get('ws-retry', 5) if isinstance(config.get('ws-retry'), int) and config.get('ws-retry') >= 0 else 5
        self.debug = config.get('debug', False)
        self.time = config.get('time', "2024.06.01")

    def default_set(self):
        from .Logger import logger
        logger.warn('框架 >>> 检测到根目录无配置文件，将进入引导模式...')
        ws = self.get_valid_ws_url()
        self.create_config_file(ws)

    def get_valid_ws_url(self):
        pattern = re.compile(r"^wss?://[^\s]+$")
        while True:
            ws = input('◈ 请输入您的正向WebSocket连接地址 >>> ')
            if not re.match(pattern, ws):
                from .Logger import logger
                logger.error('框架 >>> 您输入的值有误/为空！请重新输入')
            else:
                return ws

    def create_config_file(self, ws):
        with open(self.filepath, 'w', encoding='utf-8') as file:
            file.write(f'''# Powered by SPR-Community , Please follow the rules and readme file inside the Repository.
# 版本信息 请勿更改（用于未来可能实现的自动更新）（划掉）
version: 3.0.0 alpha-4
# 更新时间（用于菜单显示）
time: 2024.06.01

# 日志输出等级，可选值: INFO, DEBUG。值错误或此值为空则默认INFO
log-level: INFO
# 日志保存位置，值错误或此值为空则默认./logs，请注意相对/绝对路径，不要在日志文件夹结尾添加/
log-save: ./logs

# WS连接地址 仅支持正向 websocket 连接地址
ws-url: {ws}
# 连接失败重试次数。设置为0则禁止重试，值错误或此值为空则默认5
ws-retry: 5

# 插件文件夹位置
plugins-dir: ./plugins

# 调试开关（开发人员选项）
# 不建议个人用户打开，该功能打开后会默认输出消息的发包结构，请将log-level设定为DEBUG以获取详细收发包
# 大小写敏感，可选值：True,False。值错误或此值为空则默认False
debug: False

# -------以下是自定义配置的留空区，禁止删除-------''')
        from .Logger import logger
        logger.info('框架 >>> 配置文件已保存，将在5秒后自动启动框架')
        time.sleep(5)


    def read(self, key):
        """
        自定义读取配置接口
        :param key: 配置项的键
        :return: 配置项的值
        """
        try:
            with open(self.filepath, 'r', encoding='utf-8') as file:
                config = yaml.load(file, Loader=yaml.FullLoader)
                return config.get(key)
        except FileNotFoundError:
            raise FileNotFoundError("Config file not found.")
        except KeyError:
            raise KeyError(f"Key {key} not found in config.")
        

    def add(self, key, value):
        """
        自定义添加配置接口
        :param key: 配置项的键
        :param value: 配置项的值
        """
        self.config[key] = value
        with open(self.filepath, 'a+', encoding='utf-8') as file:
            lines = file.readlines()
            if lines and not lines[-1].endswith('\n'):
                lines.append('\n')
            yaml.dump(self.config, file, Dumper=yaml.Dumper, allow_unicode=True)
        from .Logger import logger
        logger.info(f'框架 >>> 新的配置项已添加: {key} = {value}')
# 创建并加载配置
config = Config()
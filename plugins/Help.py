# plugins/Help.py
from utils.Event import Event
from utils.Logger import logger
from utils.Config import config
from utils.Decorators import event_handler

__version__ = "0.0.3"
__plugin_meta__ = {
    'name': "帮助菜单",
    'description': "输出帮助菜单",
}

@event_handler
async def handle_event(group_id, text):
    if text == '/help':
        logger.event('插件管理器 >>> 开始处理命令：/help')
        help_menu = Config.help_menu_sshl if group_id in [820819698] else Config.help_menu
        await Event.send_message(help_menu)



class Config:
    version = config.version
    time = config.time
    about = f'''======================
机器人小K {version}
更新日期：{time}'''

    help_menu = f'''总菜单 | 机器人小K
==================
/help | 展示总菜单
/about | 关于信息
/ping | 测试网站信息及延迟
/motd | 查看Minecraft Java服务器在线状态
@机器人 | 与机器人聊天
{about}'''

    help_menu_sshl = f'''总菜单 | 机器人小K
==================
/help | 展示总菜单
/bind | 绑定游戏名
/unbind | 解绑游戏名
/search | 查询绑定的游戏名
/about | 关于信息
/ping | 测试网站信息及延迟
/motd | 查看Minecraft Java服务器在线状态
@机器人 | 与机器人聊天
{about}'''
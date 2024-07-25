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
async def handle_event(user_id, group_id, text):
    if text == '/help':
        logger.event('插件管理器 >>> 开始处理命令：/help')
        help_menu = Config.help_menu
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
/motd | 查看Minecraft Java服务器在线状态（测试服）
{about}'''

    help_menu_sshl = f'''总菜单 | 机器人小K
==================
/help | 展示总菜单
/bind | 绑定游戏名
/about | 关于信息
/ping | 测试网站信息及延迟
/motd | 查看Minecraft Java服务器在线状态（测试服）
{about}'''




    help_jrrp = f'''jrrp菜单 | 机器人小K
/jrrp | 获取当天人品值
/weekjrrp | 获取本周人品平均值
/monthjrrp | 获取本月人品平均值
/alljrrp | 获取所有人品平均值
{about}'''

    help_ping = f'''ping菜单 | 机器人小K
/ping <链接> | Ping指定网站/IP
/qrcode <链接> | 生成二维码链接
/whois <链接> | 查询网站所有者
{about}'''

    help_motd = f'''MC状态菜单 | 机器人小K
/motd | 获取motd-MC服务器ping菜单
/motd <服务器链接> | 查询Java版服务器状态信息
/motdpe <服务器链接> | 查询基岩版服务器状态信息
{about}'''

    help_bind = f'''绑定菜单 | 机器人小K
======================
/bind <游戏名（不加尖括号）> | 用于放行山水画路服务器及签到
{about}'''

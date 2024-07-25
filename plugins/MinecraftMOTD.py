import requests
from utils.Event import Event
from utils.Logger import logger
from utils.Decorators import event_handler
from utils.Config import config
version = config.version
date = config.time

__version__ = "0.0.3"
__plugin_meta__ = {
    'name': "Motd插件",
    'description': "检测Java Minecraft服务器的状态",
}

main_url = 'https://uapis.cn/api/mcserver?server='
back_url = 'https://api.axtn.net/api/mcserver?server='
status = 0


logger.info('MOTD插件 >>> 正在加载API')
if requests.get('https://uapis.cn/api/mcserver?server=mc.hypixel.net').status_code == 200:
    logger.info('MOTD插件 >>> API-uapis状态正常，正在检查备用API...')
    if requests.get('https://api.axtn.net/api/mcserver?server=mc.hypixel.net').status_code == 200:
        logger.info('MOTD插件 >>> API-axtn状态正常，插件启动...')
        status = 1
    else:
        logger.error('MOTD插件 >>> API-axtn状态异常，MOTD插件可能会出现问题...')
        status = 2
else:
    logger.error('MOTD插件 >>> API-uapis状态异常，正在检查备用API...')
    if requests.get('https://api.axtn.net/api/mcserver?server=mc.hypixel.net').status_code == 200:
        logger.info('MOTD插件 >>> API-axtn状态正常，插件启动...')
        status = 3
    else:
        logger.error('MOTD插件 >>> 所有API状态异常，MOTD插件出错，状态错误，即将关闭该插件...')
        status = 0



@event_handler
async def handle_event(user_id, text):
    if text.startswith('/motd '):
        logger.event('插件管理器 >>> 开始处理命令：/motd')
        if text := text[len("/motd "):]:
            if ' ' in text:
                text = text.split(' ')
                await main_func(text[0])
            else:
                await main_func(text[0:])
    elif text == '/motd' or text == '/motd ':
        await Event.send_message('使用方法：/motd IP/地址')

async def main_func(link: str):
    if link:
        if status == 0:
            await Event.send_message('API接口错误，请联系管理员')
            return
        elif status == 1 or status == 2:
            link2 = main_url + str(link)
            response = requests.get(link2)
            if response.status_code == 200:
                try:
                    response_json = response.json()
                    server = response_json['server']
                    serverstatus = response_json['status']
                    ip = response_json['ip']
                    port = response_json['port']
                    players = response_json['players']
                except requests.exceptions.JSONDecodeError:
                    await Event.send_message('服务器状态获取失败，请检查控制台')
                    return
            elif response.status_code == 500:
                if status == 1:
                    link2 = back_url + str(link)
                    response = requests.get(link2)
                    if response.status_code == 200:
                        try:
                            response_json = response.json()
                            server = response_json['server']
                            serverstatus = response_json['status']
                            ip = response_json['ip']
                            port = response_json['port']
                            players = response_json['players']
                        except requests.exceptions.JSONDecodeError:
                            await Event.send_message('服务器状态获取失败，请检查控制台')
                            return
                    elif response.status_code == 500:
                        await Event.send_message('服务器状态获取失败，可能是服务器离线？')
                        return
                elif status == 2:
                    await Event.send_message('服务器状态获取失败，可能是服务器离线？')
                    return
        elif status == 3:
            link2 = back_url + str(link)
            response = requests.get(link2)
            if response.status_code == 200:
                try:
                    response_json = response.json()
                    server = response_json['server']
                    serverstatus = response_json['status']
                    ip = response_json['ip']
                    port = response_json['port']
                    players = response_json['players']
                except requests.exceptions.JSONDecodeError:
                    await Event.send_message('服务器状态获取失败，请检查控制台')
                    return
            elif response.status_code == 500:
                await Event.send_message('服务器状态获取失败，可能是服务器离线？')
                return
        content = f'''机器人小K | 服务器状态
==========
域名：{server}
IP：{ip}
状态：{serverstatus}
端口：{port}
在线玩家：{players}
==========
机器人小K {version}
更新日期：{date}'''
        await Event.send_message(content)
            

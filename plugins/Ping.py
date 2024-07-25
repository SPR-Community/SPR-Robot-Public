import requests, socket, re
from pythonping import ping
from utils.Event import Event
from utils.Logger import logger
from utils.Config import config
from utils.Decorators import event_handler

__version__ = "0.0.3"
__plugin_meta__ = {
    'name': "Ping插件",
    'description': "测试并输出网站信息及延迟",
}

@event_handler
async def handle_event(user_id, text):
    if text == '/ping' or text == '/ping ':
        logger.event('插件管理器 >>> 开始处理命令：/ping')
        await Event.send_message('使用方法：/ping IP或域名')
        return
    elif text.startswith('/ping '):
        logger.event('插件管理器 >>> 开始处理命令：/ping')
        text = text[len("/ping "):]
        text = re.sub(r'^https://|/$', '', text)
        response = requests.get('https://uapis.cn/api/ping?host=' + text)
        if response.status_code == 200:
            response = response.json()
            host = response['host'].replace(".", ",")
            ip = response['ip'].replace(".", ",")
            location = response['location']
            maxdelay = response['max']
            mindelay = response['min']
            avgdelay = response['avg']
            message = f'''Ping | 机器人小K
============
域名：{host}
IP：{ip}
地理位置：{location}

最大延迟：{maxdelay} ms
最小延迟：{mindelay} ms
平均延迟：{avgdelay} ms
============
机器人小K {config.version}'''
        elif response.status_code == 422:
            message = '参数错误！请输入正确的IP地址/域名！'
        elif response.status_code == 500:
            await Event.send_message('API错误，请稍等，正在切换API....')
            host = text
            ip = socket.gethostbyname(text)
            result2 = ping(host)
            avgdelay = result2.rtt_avg_ms
            maxdelay = result2.rtt_max_ms
            mindelay = result2.rtt_min_ms
            response = requests.get(f'http://ip-api.com/json/{text}?fields=status,message,country,city&lang=zh-CN')
            if response.status_code == 200:
                response3 = response.json()
                country = response3['country']
                city = response3['city']
                location = country + city
                message = f'''Ping | 机器人小K
    ============
    域名：{host}
    IP：{ip}
    地理位置：{location}

    最大延迟：{maxdelay} ms
    最小延迟：{mindelay} ms
    平均延迟：{avgdelay} ms
    ============
    机器人小K {config.version}'''
            elif response.status_code == 500:
                message = 'API接口错误！请等待一段时间再尝试，如果仍无法使用，请联系管理员解决！'
        await Event.send_message(message)
            

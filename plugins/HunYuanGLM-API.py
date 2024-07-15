import requests
from utils.Event import Event
from utils.Logger import logger
from utils.Decorators import event_handler

__version__ = "0.0.1"
__plugin_meta__ = {
    'name': "混元大模型",
    'description': "使用混元模型驱动的聊天机器人",
}


url = "https://yuanqi.tencent.com/openapi/v1/agent/chat/completions"
token = "token"
appid = 'id'


headers = {
    "X-Source": "openapi",
    "Content-Type": "application/json",
    "Authorization": token
}


@event_handler
async def handle_event(user_id, text, nickname, self_id):
    if text.startswith(f'[CQ:at,qq={self_id}]'):
        logger.event('插件管理器 >>> 开始处理命令：AI...')
        data = {
            "assistant_id": appid,
            "user_id": str(user_id),
            "stream": False,
            "messages": [
                {
                    "role": "user",
                    "content": [{
                        "type": "text",
                        "text": f'[{nickname}]' + str(text)
                    }]
                }

            ]
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            res = response.json()
            choices = res.get('choices', [])
            for choice in choices:
                message = choice.get('message', {})
                content = message.get('content', '')
                await Event.send_message(content)
        else:
            await Event.send_message(f"Request failed with status code {response.status_code}: {response.text},please contact the developer")
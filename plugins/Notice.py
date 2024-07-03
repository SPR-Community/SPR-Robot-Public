from utils.Logger import logger
from utils.Event import Event
from utils.Decorators import event_handler
import time
import random

__version__ = "0.0.3"
__plugin_meta__ = {
    'name': "通知插件",
    'description': "全群广播相关内容",
}


@event_handler
async def handle_event(user_id, group_id, text):
    if text.startswith('/notice') and group_id == '群ID':
        if user_id == 3085362464:
            await Event.send_message('您当前处于黑名单中，所有事件已阻断')
            return
        logger.event('插件管理器 >>> 开始处理命令：/notice')
        text = text[len("/notice "):]
        result = await handle_notice(Event, text)
        if result == 1:
            await Event.send_message("消息发送结束！")



async def handle_notice(event: Event,message):
    group_info = await event.get_group_list()
    for group_id in group_info:
        await event.send_message(message)
        logger.info(f"发送消息至群：{group_id}")
        time.sleep(random.randint(5,7))
    logger.info("发送消息：成功")
    return 1
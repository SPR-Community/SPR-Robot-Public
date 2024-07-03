import datetime
import toml, os
from utils.Event import Event # 导入必要，所有的发信操作均于此开始
from utils.Logger import logger # 可选，可以将logger导入
from utils.Decorators import event_handler

__version__ = "0.0.2"
__plugin_meta__ = {
    'name': "广告拦截",
    'description': "拦截山水画路社区总群的广告",
}

@event_handler
async def handle_event(user_id, group_id, nickname, text, message_id):
    if not os.path.exists('./data/ad'):
        os.mkdir('./data/ad')
    files = "./data/ad/ads_" + str(datetime.date.today()) + ".toml"
    if not os.path.exists(files):
        with open(files, 'w'):
            pass
    if group_id == '检测的群' and "【广告】" in text:
        logger.info("收到广告，来自"+ nickname)
        if os.stat(files).st_size != 0:
            content = toml.load(files)
        else:
            content = {}  # 初始化
        try:
            content['ads'][str(user_id)] += 1
        except KeyError:
            # 如果用户ID不存在，初始化计数为1
            content.setdefault('ads', {})[str(user_id)] = 1

        # 检查用户是否超过广告次数限制
        if content['ads'][str(user_id)] > 3:
            logger.info(f"用户 {nickname} 已经超过3条广告！")
            try:
                await Event.delete_msg(message_id)
                message = f"[CQ:at,qq={user_id}] 您好，您当日已发送3条广告，新广告已经撤回，请注意您的广告发送限额！"
                await Event.send_message(message)
            except:
                message = f"[CQ:at,qq={user_id}] 您好，您当日已发送3条广告，消息已通知群主，请注意您的广告发送限额！"
                await Event.send_message(message)
                message2 = f'请注意，主群用户{user_id}日广告发送数超额，请各位管理及时处理！'
                await Event.send_message(message2, '管理组群')
            
        
        # 将更新的内容写回TOML文件
        with open(files, 'w') as f:
            toml.dump(content, f)
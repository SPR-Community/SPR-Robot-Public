import json
from utils.Logger import logger
from utils.Config import config
from utils.Manager import handle_event

def log_debug_info(message):
    if config.debug:
        logger.debug(f'框架 >>> {message}')

def get_nickname_card(message):
    sender = message.get('sender', {})
    card = sender.get('card', '')
    nickname = sender.get('nickname', '')
    return card if card else nickname

def get_role(message):
    role = message.get('sender', {}).get('role', '')
    return {'owner': '群主', 'admin': '群管', 'member': '群员'}.get(role, role)

async def on_message(message,botnick):
    log_debug_info(message)
    message = json.loads(message)
    sid = message['self_id']
    post_type = message['post_type']
    event_type = message.get('message_type', '')
    raw_message = message.get('raw_message', '')

    if post_type == 'meta_event':
        if message['meta_event_type'] == 'heartbeat':
            logger.debug(f'框架 >>> QQ {sid} 心跳上报更新：{message["status"]}')
        return
    
    if post_type == 'request':
        pass
    if post_type == 'notice':
        notice_type = message['notice_type']
        sub_type = message.get('sub_type', '')

        if notice_type == 'group_recall':
            if message['operator_id'] == message['user_id']:
                logger.event(f"群事件 | {message['group_id']} >>> 群成员：{message['operator_id']} 撤回了 消息ID为 {message['message_id']} 的消息")
            else:
                logger.event(f"群事件 | {message['group_id']} >>> 操作员: {message['operator_id']} 撤回了 {message['user_id']} 的消息ID为 {message['message_id']} 的消息")
        elif notice_type == 'group_increase' and sub_type in ['invite', 'approve']:
            logger.event(f"群事件 | {message['group_id']} >>> 操作员: {message['operator_id']} 同意了 {message['user_id']} 的群申请")
        elif notice_type == 'group_decrease' and sub_type == 'leave':
            if message['operator_id'] == message['user_id']:
                logger.event(f"群事件 | {message['group_id']} >>> 用户： {message['user_id']} 退群了")
            else:
                logger.event(f"群事件 | {message['group_id']} >>> 操作员: {message['operator_id']} 移除了 {message['user_id']}")
        elif notice_type == 'group_ban' and sub_type == 'ban':
            logger.event(f"群事件 | {message['group_id']} >>> 操作员：{message['operator_id']} 禁言了 {message['user_id']} ， 时长 {message['duration']}s")
        elif notice_type == 'group_ban' and sub_type == 'lift_ban':
            logger.event(f"群事件 | {message['group_id']} >>> 操作员：{message['operator_id']} 解除了 {message['user_id']} 的禁言")
        elif notice_type == 'notify' and sub_type == 'title':
            logger.event(f"群事件 | {message['group_id']} >>> 操作员：{message['title']} 移除了机器人 {message['user_id']}")
        else:
            pass
        return

    if post_type in ['message', 'message_sent']:
        message_id = message.get('message_id')
        user_id = message.get('user_id', '')
        group_id = message.get('group_id', '')
        nickname = get_nickname_card(message)
        role = get_role(message)

        if event_type == "group":
            formatted_message = f'群消息 | {group_id} | {nickname} | {user_id} | {role} >>> {raw_message}'
        elif event_type == "private":
            subtype = message.get('sub_type', '')
            mtp = '私聊' if subtype == 'friend' else '临时'
            formatted_message = f'{mtp}消息 | {user_id} | {nickname} >>> {raw_message}'
        else:
            formatted_message = f'用户消息 | 用户ID：{user_id} | 用户名：{nickname} | 消息类型：{event_type} >>> {raw_message}'

        logger.info(formatted_message)
        await handle_event(sid, user_id, group_id, nickname, event_type, None, role, raw_message, botnick, message_id)

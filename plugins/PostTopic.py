import requests
from utils.Logger import logger
from utils.Event import Event
from utils.Decorators import event_handler


__version__ = "0.0.3"
__plugin_meta__ = {
    'name': "信息推送插件",
    'description': "推送信息至山水画路社区论坛及社区总群",
}


@event_handler
async def handle_event(user_id, group_id, text):
    if text.startswith('/post ') and group_id in [903068612]:
        if user_id == 3085362464:
            await Event.send_message('您当前处于黑名单中，所有事件已阻断')
            return
        text = text[len("/post "):].split('&amp;')
        title = text[0]
        try:
            mainpara = text[1]
        except IndexError as e:
            await Event.send_message(f'您未输入正文，请重新输入，错误：{str(e)}')
            return
        result = await post(title,mainpara)
        if result != 0:
            await Event.send_message(f'帖子发布完成！详见{result}')
            await Event.send_message(title + '\r' + mainpara +'\r' + '详见' + result, 820819698)
        else:
            await Event.send_message('帖子发布失败，详见控制台')















async def post(thread_title, thread_message):
    # Xenforo论坛的API信息
    api_url = "https://forum.shanshui.site/api"
    api_key = "1icWI_URv8xwRyFW-LMZNIlhUbA-Zv05"
    forum_id = 11  # 替换为实际的板块ID

    # 构建请求头
    headers = {
        "XF-Api-Key": api_key,
        "XF-Api-User": "4"  # 使用哪个用户来发帖，通常是管理员用户ID
    }

    # 构建请求数据
    data = {
        "node_id": forum_id,
        "title": thread_title,
        "message": thread_message
    }

    # 发送POST请求以创建新帖
    response = requests.post(f"{api_url}/threads", headers=headers, data=data)

    # 检查响应状态
    if response.status_code == 200:
        result = response.json()
        if result['success'] == True:
            logger.info('发帖成功，详见' + result['thread']['view_url'])
            return result['thread']['view_url']
        else:
            logger.error(f"发帖失败: {response.status_code}")
            logger.critical(response.json())
            return 0
    else:
        logger.error(f"发帖失败: {response.status_code}")
        logger.critical(response.json())
        return 0
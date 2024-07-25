import asyncio
import requests
import os
import yaml
import time
from utils.Logger import logger, log_queue  # 导入修改后的logger和log_queue
from utils.Event import Event

now_id = 0

async def main():
    if os.path.exists('session.lock'):
        while True:
            try:
                response = requests.get('https://api.simpfun.cn/api/announcement')
                if response.status_code == 200:
                    announcements = response.json().get('list', [])
                    if announcements:
                        now_id = max(announcements, key=lambda x: x['id'])['id']
                        logger.debug(f'简幻欢-自动监听 >>> [DEBUG]最新公告ID: {now_id}')  # 使用logger记录日志
                        for announcement in announcements:
                            title = announcement.get('title')
                            text = announcement.get('text')
                            break
                        text = title + '\r\n' + text + '\r\n' + "【消息来源：简幻欢】"
                        await Event.send_message(text, 'group', 864782971)
                    else:
                        logger.warning('没有找到公告列表')

                    # 检查本地存储的默认ID
                    if not os.path.exists('./data/simpfun'):
                        os.mkdir('./data/simpfun')
                        with open('./data/simpfun/announcement.yml', 'w') as f:
                            yaml.dump({'id': now_id}, f)
                    with open('./data/simpfun/announcement.yml', 'r') as f:
                        default_id = yaml.load(f, Loader=yaml.FullLoader).get('id')

                    if now_id > default_id:
                        logger.info('简幻欢-自动监听 >>> 有新公告，正在发送')
                    else:
                        pass

                else:
                    logger.error(f'简幻欢-自动监听 >>> 请求失败，状态码：{response.status_code}')

                await asyncio.sleep(300)  # 每5分钟检查一次
            except Exception as e:
                logger.error(f'简幻欢-自动监听 >>> 发生错误: {e}')
    else:
        logger.info('检测到框架可能未启动，请先运行main.py')

# 修改__init__函数以创建事件循环运行main函数
def __init__():
    asyncio.create_task(main())  # 使用asyncio创建任务运行main函数

# 程序入口点
if __name__ == "__main__":
    __init__()
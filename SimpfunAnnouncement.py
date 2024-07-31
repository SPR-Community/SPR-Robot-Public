import asyncio
import requests
import os
import yaml
from packaging import version
from utils.Logger import logger
from utils.Event import Event

# 定义资源ID和对应的资源名称（这里假设资源ID就是公告的ID）
announcement_ids = {
    'latest_announcement_id': 0  # 假设0是初始值
}

# 检查单个公告的最新版本号并与本地存储的版本号比较
async def check_announcement_version(announcement_id):
    # 这里假设API的URL和参数
    api_url = 'https://api.simpfun.cn/api/announcement'
    try:
        response = requests.get(api_url, headers={'Cache-Control': 'no-cache'})
        response.raise_for_status()  # 如果响应状态码不是200，将抛出HTTPError异常
        announcements = response.json().get('list', [])
        if announcements:
            latest_announcement = max(announcements, key=lambda x: x['id'])
            latest_announcement_id = latest_announcement['id']

            # 检查本地存储的默认ID
            version_file_path = './data/simpfun/announcement.yml'
            if not os.path.exists('./data/simpfun'):
                os.mkdir('./data/simpfun')

            default_announcement_id = None
            if os.path.exists(version_file_path):
                with open(version_file_path, 'r') as f:
                    default_announcement_id = yaml.load(f, Loader=yaml.FullLoader).get('latest_announcement_id')

            # 使用packaging.version进行版本比较（这里假设比较的是ID）
            if version.parse(str(latest_announcement_id)) != version.parse(str(default_announcement_id or '0')):
                logger.info('简幻欢-自动监听 有新公告，正在发送')
                # 这里获取最新的公告内容
                announcement_content = await get_announcement_content(latest_announcement)
                await Event.send_message(announcement_content, 864782971, 'group')

                # 更新本地存储的版本号
                with open(version_file_path, 'w') as f:
                    yaml.dump({'latest_announcement_id': latest_announcement_id}, f)
            else:
                logger.debug('无新公告')
        else:
            logger.warning('没有找到公告列表')

    except requests.HTTPError as http_err:
        logger.error(f'简幻欢-自动监听 请求失败，状态码：{http_err.response.status_code}')
    except Exception as e:
        logger.error(f'简幻欢-自动监听 发生错误: {e}')

# 异步函数，用于获取最新的公告内容
async def get_announcement_content(announcement):
    # 这里假设获取公告内容的逻辑
    title = announcement.get('title')
    text = announcement.get('text')
    content = f'{title}\r\n{text}\r\n【消息来源：简幻欢】'
    return content

# 主循环，定时检查所有资源的版本
async def main():
    if os.path.exists('session.lock'):
        while True:
            await check_announcement_version(announcement_ids['latest_announcement_id'])
            await asyncio.sleep(300)  # 每5分钟检查一次

    else:
        logger.info('检测到框架可能未启动，请先运行main.py')

# 初始化函数，创建事件循环运行main函数
def __init__():
    asyncio.create_task(main())

# 程序入口点
if __name__ == "__main__":
    __init__()

import asyncio
import requests
import os
import yaml
from packaging import version
from utils.Logger import logger
from utils.Event import Event

# 定义SpigotMC资源的更新URL和版本检查URL模板


# 定义资源ID和对应的资源名称
resource_ids = {
    'AkariLevel': 116936,
    'AkariBan': 117132,
    'AkariCDK': 117225,
}
ghrurl = 'https://api.github.com/repos/CPJiNan/{}/commits'

# 检查单个资源的最新版本号并与本地存储的版本号比较
async def check_resource_version(resource_name, resource_id):
    update_url = 'https://www.spigotmc.org/resources/'
    version_url = 'https://api.spigotmc.org/legacy/update.php?resource='
    version_url = version_url + str(resource_id)
    try:
        response = requests.get(version_url)
        response.raise_for_status()  # 如果响应状态码不是200，将抛出HTTPError异常
        latest_version = response.text.strip()
        if latest_version:
            version_file_path = f'./data/SpigotMC/{resource_name}.yml'

            if not os.path.exists('./data/SpigotMC'):
                os.mkdir('./data/SpigotMC')

            default_version = None
            if os.path.exists(version_file_path):
                with open(version_file_path, 'r') as f:
                    default_version = yaml.load(f, Loader=yaml.FullLoader).get('version')

            # 使用packaging.version进行版本比较
            if version.parse(latest_version) > version.parse(default_version or '0.0.0'):
                logger.info(f'SpigotMC >> 资源{resource_name}有更新，正在收集log并提交...')
                commit_message = await get_repo_commit(resource_name)
                text = f'【版本更新】SpigotMC资源更新\r\n{resource_name}更新至{latest_version}\r\n\r\n本次更新内容如下：\r\n{commit_message}\r\n\r\n点击链接下载\r\n{update_url}{resource_id}'
                await Event.send_message(text, 704109949, 'group')

                # 更新本地存储的版本号
                with open(version_file_path, 'w') as f:
                    yaml.dump({'version': latest_version}, f)
            else:
                logger.debug(f'{resource_name} 无更新')
        else:
            logger.warning(f'SpigotMC >> 没有找到{resource_name}的资源ID')
    except requests.HTTPError as http_err:
        logger.error(f'SpigotMC >> {resource_name}请求失败，状态码：{http_err.response.status_code}')
    except Exception as e:
        logger.error(f'SpigotMC >> 检查{resource_name}版本时发生错误: {e}')





async def get_repo_commit(resource_name):
    url = ghrurl.format(resource_name)
    try:
        response = requests.get(url)
        response.raise_for_status()  # 如果响应状态码不是200，将抛出HTTPError异常
        commits = response.json()
        if commits:
            commit = commits[0]
            commit_message = commit['commit']['message']
            commit_message = commit_message.replace('\n', '\r\n')
    except requests.HTTPError as http_err:
        logger.error(f'SpigotMC >> {resource_name}请求失败，状态码：{http_err.response.status_code}')
        commit_message = f'日志获取失败 错误码{http_err.response.status_code}'
    except Exception as e:
        logger.error(f'SpigotMC >> 检查{resource_name}日志时发生错误: {e}')
        commit_message = f'日志获取失败 错误：{e}'
    return commit_message



# 主循环，定时检查所有资源的版本
async def main():
    if os.path.exists('session.lock'):
        while True:
            for resource_name, resource_id in resource_ids.items():
                await check_resource_version(resource_name, resource_id)
                await asyncio.sleep(10)  # 简短延迟，避免过快请求

            await asyncio.sleep(7200)  # 每2小时检查一次

    else:
        logger.info('检测到框架可能未启动，请先运行main.py')

# 初始化函数，创建事件循环运行main函数
def __init__():
    asyncio.create_task(main())

# 程序入口点
if __name__ == "__main__":
    __init__()





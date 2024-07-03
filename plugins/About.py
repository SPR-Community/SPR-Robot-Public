from utils.Event import Event
from utils.Logger import logger
from datetime import datetime, timedelta
from utils.Decorators import event_handler
import psutil, platform, os

message_count = 0
project_start_time = datetime.now()

__version__ = "0.0.3"
__plugin_meta__ = {
    'name': "关于插件",
    'description': "将当前的机器人信息输出",
}


@event_handler
async def handle_event(self_id, user_id, group_id, text, botnick):
    global message_count
    message_count = message_count + 1
    if text == '/about':
        if user_id == 3085362464:
            await Event.send_message('您当前处于黑名单中，所有事件已阻断')
            return
        logger.event('插件管理器 >>> 开始处理命令：/about')
        await handle_about(self_id, botnick, group_id, message_count)


async def handle_about(self_id, botnick, group_id, message_count):
    booted = await get_header_data()
    current_time = datetime.now()
    global project_start_time
    elapsed_time = current_time - project_start_time
    days = elapsed_time.days
    hours, remainder = divmod(elapsed_time.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    elapsed_time = f'{days} 天 {hours} 小时 {minutes} 分钟 {seconds} 秒'
    about = f'''机器人小K | 关于信息
===========
Bot昵称：{botnick}
Bot UID：{self_id}
当前Bot协议：OneBot V11
操作系统：{await get_system_name()}

系统运行时间：{booted}
框架运行时间：{elapsed_time}

消息收/发： {message_count} 条

===========
时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Copyright 2024 山水画路社区'''
    await Event.send_message(about)





async def format_timedelta(t: timedelta):
    mm, ss = divmod(t.seconds, 60)
    hh, mm = divmod(mm, 60)
    s = f"{hh}时{mm:02d}分{ss:02d}秒"
    if t.days:
        s = f"{t.days}天 {s}"
    return s

async def get_header_data():
    now_time = datetime.now()
    booted = await format_timedelta(
        now_time - datetime.fromtimestamp(psutil.boot_time()),
    )
    return booted
async def get_system_name():
    system, _, release, version, machine, _ = platform.uname()
    system, release, version = platform.system_alias(system, release, version)

    if system == "Java":
        _, _, _, (system, release, machine) = platform.java_ver()

    if system == "Darwin":
        return f"MacOS {platform.mac_ver()[0]} {machine}"

    if system == "Windows":
        return f"Windows {release} {platform.win32_edition()} {machine}"

    if system == "Linux":
        if (pfx := os.getenv("PREFIX")) and "termux" in pfx:
            system = f"Termux (Android) {release}"  # a strange platform

        elif os.getenv("ANDROID_ROOT") == "/system":
            system = f"Linux (Android) {release}"
        else:
            system = f"未知 Linux {release}"

        return f"{system} {machine}"

    return f"{system} {release}"
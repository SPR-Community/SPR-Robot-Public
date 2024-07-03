import sqlite3, os
from utils.Logger import logger
from utils.Event import Event
from plugins.Rcon import *
import re
from utils.Decorators import event_handler

__version__ = "0.0.3"
__plugin_meta__ = {
    'name': "绑定插件",
    'description': "绑定/解绑/查询用户在山水画路社区服务器所持有账户的插件",
}

@event_handler
async def handle_event(user_id, group_id, text):
    if text.startswith("/bind ") and group_id in '群ID':
        if user_id == 3085362464:
            await Event.send_message('您当前处于黑名单中，所有事件已阻断')
            return
        else:
            pass
        logger.event('插件管理器 >>> 开始处理命令：/bind')
        if text := text[len("/bind "):]:
            if 'YiLonger_' in text or user_id == '':
                await Event.send_message(f"禁止绑定此账户！此账户位于黑名单")
                return
            result = await main_bind(text, user_id)
            if result == 0:
                alluser = await get_player_names(user_id)
                await Event.send_message(f"绑定完毕！\n======\n您当前绑定的玩家为：{text}\n您当前绑定的所有玩家： {alluser} ")
            else:
                await Event.send_message(result)
    elif text.startswith("/unbind ") and group_id in '群ID':
        if user_id == 3085362464:
            await Event.send_message('您当前处于黑名单中，所有事件已阻断')
            return
        logger.event('插件管理器 >>> 开始处理命令：/unbind')
        if text := text[len("/unbind "):]:
            await Event.send_message(await delete_player(user_id,text))
    elif text == "/search" and group_id in '群ID':
        if user_id == 3085362464:
            await Event.send_message('您当前处于黑名单中，所有事件已阻断')
            return
        logger.event('插件管理器 >>> 开始处理命令：/search')
        await Event.send_message(f"查询完毕！\n======\n您当前绑定的玩家有：" + await get_player_names(user_id))


if not os.path.exists('./data'): # 检查目录
    os.mkdir('./data')

if not os.path.exists('./data/bind.db'): # 检查数据库，不存在则创建
    logger.warning('绑定插件 >>> 数据库不存在，正在尝试初始化新数据库') # Logger一下
    conn = sqlite3.connect('./data/bind.db', check_same_thread=False) # 游标连接
    cursor = conn.cursor() # 指针
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                qq_number INTEGER NOT NULL,
                player_name TEXT NOT NULL UNIQUE
            )
        """) # 表
        conn.commit() # 提交
        logger.info("绑定插件 >>> 数据库初始化成功！") # 发消息
    
    except sqlite3.Error as e:
        logger.error(f"数据库初始化失败：{e}") # 发报错
    finally:
        if conn:
            conn.close() # 关游标

# 创建数据库连接和游标
conn = sqlite3.connect('./data/bind.db', check_same_thread=False)
cursor = conn.cursor()

async def delete_player(qq_number: int, player_name: str) -> str: # 删除用户
    """删除指定QQ号下的特定用户名"""
    try:
        # 检查该QQ号下是否存在指定的用户名
        cursor.execute("SELECT id FROM players WHERE qq_number = ? AND player_name = ?", (qq_number, player_name))
        result = cursor.fetchone()
        if result:
            res = await unreg(player_name)
            if res == 'True':
                player_id = result[0]
                cursor.execute("DELETE FROM players WHERE id = ?", (player_id,))
                conn.commit()
                return f'''成功删除玩家 {player_name}
请注意，玩家删除后一周以内若不再重新绑定，将【删除】账户的所有权限组、物品以及登录密码等信息
如需恢复，请在一周内重新绑定此账户以避免数据丢失！'''
            else:
                return res

        else:
            return f"未找到玩家 {player_name} 或该玩家不属于QQ号 {qq_number}"
    except sqlite3.Error as e:
        return f"删除玩家失败：{e}"

async def main_bind(player_name: str, qq_number: int) -> str:
    """绑定QQ号和玩家名"""
    if len(player_name) < 3 or len(player_name) > 17:
        return '绑定失败！用户名应长度为3-17个字符！'
    elif not re.match(r'^[a-zA-Z0-9_]+$', player_name):
        return '绑定失败！用户名只能是由英文、数字、下划线组成的内容！'
    cursor.execute("SELECT COUNT(*) FROM players WHERE qq_number = ?", (qq_number,))
    count = cursor.fetchone()[0]
    if count >= 3:
        return '绑定失败！一个QQ号最多只能绑定三个玩家，您当前已经绑定了三个玩家'
    cursor.execute("SELECT 1 FROM players WHERE LOWER(player_name) = LOWER(?)", (player_name,))
    if cursor.fetchone():
        return '绑定失败！该玩家名已被其他账户绑定.'
    try:
        res = await reg(player_name)
        if res == 'True':
            cursor.execute("INSERT INTO players (qq_number, player_name) VALUES (?, ?)", (qq_number, player_name))
            conn.commit()
            return 0
        else:
            return res
    except sqlite3.IntegrityError:
        return '绑定失败！数据库错误。'
    
async def get_player_names(qq_number: int) -> str:
    """查询指定QQ号绑定的所有用户名，并以逗号分隔的形式返回"""
    try:
        # 查询指定QQ号绑定的所有用户名
        cursor.execute("SELECT player_name FROM players WHERE qq_number = ?", (qq_number,))
        results = cursor.fetchall()
        
        # 将查询结果格式化为逗号分隔的字符串
        player_names = ', '.join([result[0] for result in results])
        if player_names:
            return player_names
        else:
            return "无"
    
    except sqlite3.Error as e:
        return f"查询玩家失败：{e}"
    



async def reg(player_name):
    try:
        注册玩家 =await  MinecraftClient.connect(host="host",port=1,pasw="")
        结果 = await 注册玩家.command(f'playerwhitelist add {player_name}')
        await 注册玩家.close()
        正式结果 = re.sub("§.", "", 结果)
        if "已添加玩家" in 正式结果:
            return "True"
    except RconBaseError as e:
        logger.error("Rcon无法连接 - 绑定失败")
        return '''无法绑定：
服务器目前无响应，可能是远程节点崩溃或其他问题导致，请等待几分钟后重试
本次绑定已作废，若多次出现此现象，请联系管理员'''

async def unreg(player_name):
    try:
        注册玩家 = await MinecraftClient.connect(host="host",port=1,pasw='')
        结果 = await 注册玩家.command(f'playerwhitelist remove {player_name}')
        await 注册玩家.close()
        正式结果 = re.sub("§.", "", 结果)
        if "从白名单删除" in 正式结果:
            return "True"
    except RconBaseError as e:
        logger.error("Rcon无法连接 - 解绑失败")
        return '''无法解绑：
服务器目前无响应，可能是远程节点崩溃或其他问题导致，请等待几分钟后重试
本次绑定已作废，若多次出现此现象，请联系管理员'''

import websockets
import asyncio, json
from core import on_message
from utils.Logger import logger, logging, on_stop
from utils.Manager import load_plugins
from utils.Config import config
import os

dir = os.path.dirname(__file__)

async def stop(ws=None):
    logger.info("框架 >>> 正在关闭监听......")
    if ws:
        await ws.close()
    logger.info("框架 >>> 正在关闭日志记录器......")
    logging.shutdown()
    await on_stop()
    os._exit(0)

async def handle_websocket(ws):
    try:
        async with websockets.connect(config.url) as websocket:
            info = json.loads(await websocket.recv())
            if info['sub_type'] == 'connect':
                get_login_info = {"action": "get_login_info", "params": {}}
                await websocket.send(json.dumps(get_login_info))
                info = json.loads(await websocket.recv())
                uid = info['data']['user_id']
                nickname = info['data']['nickname']
                logger.info(f'框架 >>> QQ {uid} 已连接')
                logger.info(f'框架 >>> 欢迎您，{nickname}！')
        
        async for message in ws:
            await on_message(message,nickname)
    
    except websockets.exceptions.ConnectionClosed:
        await handle_reconnection()
    except asyncio.CancelledError:
        await stop(ws)

async def handle_reconnection():
    logger.warning("框架 >>> WebSocket 连接被关闭，正在尝试重连")
    reconnect_attempts = config.retry
    if reconnect_attempts != 0:
        for attempt in range(1, reconnect_attempts + 1):
            if await attempt_reconnect(attempt, reconnect_attempts):
                break
        else:
            await stop()
    else:
        await attempt_reconnect()

async def attempt_reconnect(attempt=0, max_attempts=0):
    try:
        async with websockets.connect(config.url) as ws:
            await handle_websocket(ws)
            return True
    except (ConnectionRefusedError, websockets.exceptions.WebSocketException) as e:
        logger.error(f'框架 >>> 连接失败：{e}')
        if attempt < max_attempts:
            logger.warning(f'框架 >>> 正在尝试重连 {attempt}/{max_attempts}...')
            await asyncio.sleep(5)
        else:
            logger.error('框架 >>> Websocket连接失败，即将退出...')
        return False

async def connect_and_run():
    version = config.version
    logger.info(f'框架 >>> 框架已启动 当前框架版本：SPR-Robot:{version}')
    if config.debug:
        logger.warning(f'框架 >>> 开发者模式已启动，如果您不是开发人员，请将config.yml中的debug设为False')
    
    logger.info('插件管理器 >>> 开始加载插件......')
    await load_plugins(dir)
    logger.info('插件管理器 >>> 加载完毕')

    reconnect_attempts = config.retry
    if reconnect_attempts != 0:
        for attempt in range(1, reconnect_attempts + 1):
            if await attempt_reconnect(attempt, reconnect_attempts):
                break
        else:
            await stop()
    else:
        await attempt_reconnect()

async def main():
    await connect_and_run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        asyncio.run(stop())
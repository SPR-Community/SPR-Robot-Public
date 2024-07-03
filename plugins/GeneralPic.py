import string
from typing import List, Optional, Tuple, TypeVar, cast

import dns.asyncresolver
import dns.name
import dns.rdatatype as rd
from dns.rdtypes.IN.SRV import SRV as SRVRecordAnswer  # noqa: N811
from PIL import Image, ImageDraw, ImageFont
import requests, os
from utils.Event import Event
from mcstatus import BedrockServer, JavaServer
from mcstatus.status_response import JavaStatusResponse
from utils.Logger import logger
from utils.Decorators import event_handler

RANDOM_CHAR_TEMPLATE = f"{string.ascii_letters}{string.digits}!§$%&?#"
WHITESPACE_EXCLUDE_NEWLINE = string.whitespace.replace("\n", "")
DNS_RESOLVER = dns.asyncresolver.Resolver()
DNS_RESOLVER.nameservers = [*DNS_RESOLVER.nameservers, "1.1.1.1", "1.0.0.1"]

T = TypeVar("T")

status = None
font_path = "./data/motd/unifont.ttf"
width, height = 800, 0
padding = 10
max_text_width = 0

__version__ = "0.0.2"
__plugin_meta__ = {
    'name': "Motd插件",
    'description': "生成Java Minecraft服务器的状态图片",
}

def prepare_func():
    logger.warn('MOTD >> 未检测到字体文件，正在尝试拉取字体文件（https://spr-community.github.io/SPR-Robot-SRC/motd/font/unifont.ttf）')
    get_text = requests.get('https://spr-community.github.io/SPR-Robot-SRC/motd/font/unifont.ttf')
    if get_text.status_code == 200:
        with open('./data/motd/unifont.ttf', 'wb') as f:
            f.write(get_text.content)
    else:
        logger.error('MOTD >> 拉取失败：返回code错误，请主动访问 https://spr-community.github.io/SPR-Robot-SRC/motd/font/unifont.ttf 下载该字体文件并放入./data/motd目录中！否则可能造成生成问题')
    logger.info('MOTD >> 正在检测API是否正常(1/1)...')
    global status 
    response = requests.get('https://uapis.cn/api/mcserver?server=mc.hypixel.net')
    if response.status_code == 200:
        logger.info('MOTD >> 查询API正常，状态设置为True，MOTD插件已经准备就绪！')
        status = True
    else:
        logger.error(f'MOTD >> API错误，返回码{response.status_code}，请联系管理员或检查该API是否正常：https://uapis.cn/api/mcserver?server=mc.hypixel.net')
        status = False

logger.info('MOTD >> 正在检查文件是否完整...')
if not os.path.exists('./data/motd'):
    logger.warn('MOTD >> 未检测到/data/motd文件夹，正在创建...')
    os.mkdir('./data/motd')
    prepare_func()
if not os.path.exists('./data/motd/unifont.ttf'):
    prepare_func()
logger.info('MOTD >> 文件检查完毕')



@event_handler
async def handle_event(user_id, group_id, text):
    if text.startswith('/motd '):
        if user_id == 3085362464:
            await Event.send_message('您当前处于黑名单中，所有事件已阻断')
            return
        logger.event('插件管理器 >>> 开始处理命令：/motd')
        if text := text[len("/motd "):]:
            if ' ' in text:
                text = text.split(' ')
                await main_func(text[0], group_id, text[1:])
            else:
                await main_func(text[0:], group_id, 'je')
    elif text == '/motd' or text == '/motd ':
        await Event.send_message('使用方法：/motd IP地址')

async def main_func(link: str, group_id: int, stattype: str = 'je' or 'be' or None):
    is_java = (stattype == 'je')
    
    if link:
        ip, port = await resolve_ip(link, is_java)
        link = f'https://uapis.cn/api/mcserver?server={link}'
        response = requests.get(link)
        if response.status_code == 200:
            try:
                response_json = response.json()
                img = response_json['img']
            except requests.exceptions.JSONDecodeError:
                img = "https://spr-community.github.io/SPR-Robot-SRC/motd/defaulticon.png"
        else:
            img = "https://spr-community.github.io/SPR-Robot-SRC/motd/defaulticon.png"
        
        if await draw(ip, port, img, group_id, is_java):
            image = os.path.join(os.getcwd(), 'data', 'motd', 'temp2.png')
            await Event.send_message(f'[CQ:image,file=file:///{image}]')
            os.remove(image)

async def resolve_srv(host: str) -> Tuple[str, int]:
    host = "_minecraft._tcp." + host
    resp = await DNS_RESOLVER.resolve(host, rd.SRV)
    answer = cast(SRVRecordAnswer, resp[0])
    return str(answer.target), int(answer.port)

async def resolve_host(
    host: str,
    data_types: Optional[List[rd.RdataType]] = None,
) -> Optional[str]:
    data_types = data_types or [rd.CNAME, rd.AAAA, rd.A]
    for rd_type in data_types:
        try:
            resp = (await DNS_RESOLVER.resolve(host, rd_type)).response
            name = resp.answer[0][0].to_text()  # type: ignore
        except Exception as e:
            logger.debug(
                f"Failed to resolve {rd_type.name} record for {host}: "
                f"{e.__class__.__name__}: {e}",
            )
        else:
            logger.debug(f"Resolved {rd_type.name} record for {host}: {name}")
            if rd_type is rd.CNAME:
                return await resolve_host(name)
            return name
    return None

async def resolve_ip(ip: str, srv: bool = False) -> Tuple[str, Optional[int]]:
    if ":" in ip:
        host, port = ip.split(":", maxsplit=1)
    else:
        host = ip
        port = None

    if (not port) and srv:
        try:
            host, port = await resolve_srv(host)
        except Exception as e:
            logger.debug(
                f"Failed to resolve SRV record for {host}: "
                f"{e.__class__.__name__}: {e}",
            )
        logger.debug(f"Resolved SRV record for {ip}: {host}:{port}")

    return (
        await resolve_host(host) or host,
        int(port) if port else None,
    )

async def get_result(svr: JavaStatusResponse):
    motd = svr.motd.to_plain()
    people = f"{svr.players.online}/{svr.players.max} ({svr.players.online/svr.players.max * 100:.2f}%)"
    delay = round(svr.latency, 2)
    version = svr.version.name
    detail = svr.version.protocol
    return motd, version, detail, people, delay

async def draw(host, port, img, group_id, is_java: bool = True):
    global font_path, width, height, padding, max_text_width
    svr = JavaServer(host, port) if is_java else BedrockServer(host, port)
    try:
        await svr.async_status()
        motd, version, detail, people, delay = await get_result(await svr.async_status())
    except OSError as e:
        await Event.send_message(f'请求出错！具体错误：{e}')
        return
    line_x = width // 3
    texts = [
        {"text": "[MC服务器信息]", "font_size": 30, "color": '#FFFFFF', "x": line_x + padding, "y": 30},
        {"text": "请求成功", "font_size": 20, "color": (0, 255, 0), "x": width - padding, "y": padding, "align": "right"},
        {"text": motd, "font_size": 35, "color": (255, 255, 255), "x": line_x + padding, "y": 110},
        {"text": f"服务端名: {version}", "font_size": 30, "color": (255, 255, 255), "x": line_x + padding, "y": 340},
        {"text": f"协议版本: {detail}", "font_size": 30, "color": (255, 255, 255), "x": line_x + padding, "y": 370},
        {"text": f"当前人数: {people}", "font_size": 30, "color": (255, 255, 255), "x": line_x + padding, "y": 400},
        {"text": f"测试延迟: {delay}ms", "font_size": 30, "color": (0, 255, 0), "x": line_x + padding, "y": 430},
    ]

    for text_info in texts:
        font = ImageFont.truetype(font_path, text_info["font_size"])
        bbox = font.getbbox(text_info["text"])
        text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
        if text_info["y"] + text_height + padding > height:
            height = text_info["y"] + text_height + padding
        if text_width > max_text_width:
            max_text_width = text_width

    width = max(width, max_text_width + line_x + 2 * padding)
    height += padding
    background = Image.new('RGB', (width, height), color=(73, 109, 137))
    draw = ImageDraw.Draw(background)
    draw.line((line_x, 0, line_x, height), fill=(255, 255, 255), width=2)
    response = requests.get(img)
    if response.status_code == 200:
        with open(os.getcwd() + '\\data\\motd\\temp.png', 'wb') as f:
            f.write(response.content)

    insert_img = Image.open(os.getcwd() + '\\data\\motd/temp.png').convert('RGBA')
    insert_img = insert_img.resize((line_x - 2 * padding, line_x - 2 * padding))
    insert_x = (line_x - insert_img.width) // 2
    insert_y = (height - insert_img.height) // 2
    background.paste(insert_img, (insert_x, insert_y), insert_img)
    for text_info in texts:
        font = ImageFont.truetype(font_path, text_info["font_size"])
        if text_info.get("align") == "right":
            bbox = font.getbbox(text_info["text"])
            text_width = bbox[2] - bbox[0]
            draw.text((text_info["x"] - text_width, text_info["y"]), text_info["text"], font=font, fill=text_info["color"])
        else:
            draw.text((text_info["x"], text_info["y"]), text_info["text"], font=font, fill=text_info["color"])

    # 裁剪图片，去掉右侧多余的空白部分
    bbox = background.getbbox()
    cropped_background = background.crop(bbox)

    output_path = os.path.join(os.getcwd(), 'data', 'motd', 'temp2.png')
    cropped_background.save(output_path)
    os.remove(os.path.join(os.getcwd(), 'data', 'motd', 'temp.png'))
    return True

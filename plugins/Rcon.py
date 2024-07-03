from asyncio import open_connection,StreamReader,StreamWriter,sleep
from typing import Optional
import struct

class RconBaseError(Exception):
    """Rcon错误"""
    def __init__(self, msg):
        super().__init__()
        self.msg = msg

class ClientError(RconBaseError):
    """链接错误"""
    pass

class InvalidPassword(RconBaseError):
    """登陆错误"""
    pass


class Rcon:
    END = b'\x00\x00'
    """结束符"""

    class PacketType:
        """发送类型"""

        AUTH = 3
        """登陆"""
        COMMAND = 2
        """命令"""
        CHAT = 1
        """聊天"""
        SEND = 0
        """发包"""
    
    @staticmethod
    def build_packet(packet_type:'Rcon.PacketType', data:str):
        """构建数据包"""
        out = struct.pack('<li', 0, packet_type) + data.encode('utf8') + Rcon.END

        out_len = struct.pack('<i', len(out))
        return out_len + out
        ...

    @staticmethod
    def command(cmd:str):
        """构建命令数据"""
        return Rcon.build_packet(Rcon.PacketType.COMMAND, cmd)
        ...
    
    @staticmethod
    def auth(pasw:str):
        """构建登陆数据"""
        return Rcon.build_packet(Rcon.PacketType.AUTH, pasw)
        ...

class MinecraftClient:
    host:Optional[str]
    port:Optional[int]
    pasw:Optional[str]

    _reader:Optional[StreamReader]
    _writer:Optional[StreamWriter]
    
    auth_state:bool = False
    """是否登陆"""
    init_state:bool = False
    """是否初始化"""


    def __init__(self, host:str, port:int, pasw:str):
        self.host = host
        self.port = port
        self.pasw = pasw

        self._reader:StreamReader = None
        self._writer:StreamWriter = None

        self.init_state = True
    
    
    async def _read_data(self,leng):
        """读取数据"""

        data = b''
        while len(data) < leng:
            data += await self._reader.read(leng - len(data))

        return data
    
    async def _read(self):
        """读取并解析数据"""
        
        result_len, *_ = struct.unpack('<i', await self._read_data(4))
        result_value = await self._read_data(result_len)

        packet_id, packet_type = struct.unpack('<ii', result_value[:8])
        packet_data, packet_end = result_value[8:-2], result_value[-2:]

        if packet_end != b'\x00\x00':
            raise ClientError('链接异常！')
        
        if packet_id == -1:
            raise InvalidPassword('密码无效！')

        data = packet_data.decode('utf8')
        return data

    async def _send(self, packet):
        """发送数据包, 并返回结果"""

        if not self._writer:
            raise ClientError('尚未创建链接, 请使用connect方法创建链接！')
        
        # 发送数据
        self._writer.write(packet)
        return await self._read()



    async def _connect(self):
        """创建链接"""

        if not self.init_state:
            raise ClientError('尚未初始化, 请使用connect方法创建链接！')

        if self.auth_state:
            raise ClientError('已登陆, 请直接使用send方法发送数据！')
        
        try:
            self._reader, self._writer = await open_connection(self.host, self.port)
        except OSError as e:
            raise ClientError('无法创建链接: {}'.format(e))
        
    async def __aenter__(self):
        await self._connect()
        await self.auth()

        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    @classmethod
    async def connect(cls, *,host, port, pasw):
        """初始化链接并登陆, 返回链接对象"""
        self = cls(host, port, pasw)

        # 创建链接
        await self._connect()
        # 登陆
        await self.auth()

        return self
    
    async def close(self):
        """关闭链接"""
        if self._writer:
            self._writer.close()
            self._writer = None
            self._auth = False
    
    async def auth(self,pasw:str = None):
        pasw = pasw or self.pasw

        """登陆"""
        if not self.auth_state:
            packet = Rcon.auth(pasw)
            await self._send(packet)
            self.auth_state = True

    async def command(self, command):
        """发送命令"""
        packet = Rcon.command(command)
        return await self._send(packet)
    
    async def say(self, message):
        """发送聊天"""
        await self.command(f"say {message}")



# 上下文用法
# async with MinecraftClient(host='localhost', port=25575, pasw='AABBCC') as client:
    
#     result = await client.say('weather rain')
#     print(result)

#     result = await client.command('help')
#     print(result)


# 简单用法
# client = await MinecraftClient.connect(host='localhost', port=25575, pasw='AABBCC')

# result = await client.say('weather rain')
# print(result)

# result = await client.command('help')
# print(result)

# await client.close()
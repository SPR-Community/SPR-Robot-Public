import websockets
import json
from .Config import Config
from .Logger import logger
config = Config()

class Event:
    async def send_message(message: str, id: int = None, send_type: str = None, websocket_url: str = config.url):
        """
        发送消息函数

        Parameters:
        - message: str，消息内容
        - id: int，群号/用户QQ号
        - send_type: str，发送类型，可选值为 "group" 或 "private"
        - websocket_url: str，WebSocket 服务器地址，默认为配置文件中的URL
        
        Raises:
        - TypeError: 发送类型错误
        - ConnectionError: 连接错误
        - SendMessageError: 发送消息失败
        """
        from .Decorators import current_id, current_send_type
        if id is None:
            id = current_id
        if send_type is None:
            send_type = current_send_type
        if send_type == "group":
            event_data = {
                "action": "send_msg",
                "params": {
                    "message_type": "group",
                    "group_id": id,
                    "message": message
                }
            }
        elif send_type == "private":
            event_data = {
                "action": "send_msg",
                "params": {
                    "message_type": "private",
                    "user_id": id,
                    "message": message
                }
            }
        else:
            raise TypeError("Send Error: Type 'send_type' error.")
        try:
            logger.debug(event_data)
            async with websockets.connect(websocket_url) as websocket:
                await websocket.send(json.dumps(event_data))
                await websocket.recv()
                result = await websocket.recv()
                logger.debug(result)
        except websockets.exceptions.WebSocketException:
            raise ConnectionError("Send error: Unable to connect to WebSocket server.")
        except Exception as e:
            raise SendMessageError("Send error: " + str(e))
        return
    async def get_group_list(websocket_url: str = config.url):
        event_data = {
            "action": "get_group_list",
            "params": {}
        }

        try:
            async with websockets.connect(websocket_url) as websocket:
                await websocket.send(json.dumps(event_data))
                await websocket.recv()
                result = await websocket.recv()
                response = json.loads(result)
                
                if response.get('status') == 'ok':
                    group_ids = {item['group_id']: item for item in response.get('data', [])}
                    group_ids = {group_id for group_id in group_ids}
                    return group_ids
                else:
                    error_message = response.get('message', 'Unknown error')
                    raise GetInfoError(f"Error from server: {error_message}")

        except websockets.exceptions.WebSocketException as wse:
            raise ConnectionError(f"WebSocket error: {str(wse)}")
        
        except json.JSONDecodeError as jde:
            raise GetInfoError(f"JSON decoding error: {str(jde)}")
        
        except GetInfoError as ge:
            # Log detailed error message
            logger.error(f"GetInfoError in get_group_list(): {str(ge)}")
            raise  # Re-raise the exception to propagate it further
        except Exception as e:
            logger.error(f"Unexpected error in get_group_list(): {str(e)}")
            raise GetInfoError(f"Get error: {str(e)}")
        return
    async def delete_msg(message_id: int, websocket_url: str = config.url):
        """
        撤回消息函数

        Parameters:
        - message_id: int，消息ID

        
        Raises:
        - ConnectionError: 连接错误
        """
        event_data = {
            "action": "delete_msg",
            "params": {
                "message_id": message_id
            }
        }
        try:
            async with websockets.connect(websocket_url) as websocket:
                await websocket.send(json.dumps(event_data))
        except websockets.exceptions.WebSocketException:
            raise ConnectionError("Send error: Unable to connect to WebSocket server.")
        return
    async def upload_files(group_id:int, path: str = None, websocket_url: str = config.url):
        """
        上传文件函数

        Parameters:
        - name: str，文件上传名称
        - path: str，文件在源路径

        
        Raises:
        - ConnectionError: 连接错误
        - GetInfoError: 图片ID错误
        """
        event_data = {
            "action": "upload_group_file",
            "params": {
                "group_id": group_id,
                "file": path
            }
        }
        try:
            async with websockets.connect(websocket_url) as websocket:
                await websocket.send(json.dumps(event_data))
                await websocket.recv()
                result = json.loads(await websocket.recv())
                if result.get('status') == 'ok':
                    return True
                else:
                    error_message = result.get('message', 'Unknown error')
                    raise GetInfoError(f"Error from server: {error_message}")
        except websockets.exceptions.WebSocketException as wse:
            raise ConnectionError(f"WebSocket error: {str(wse)}")
        
        except json.JSONDecodeError as jde:
            raise GetInfoError(f"JSON decoding error: {str(jde)}")
        
        except GetInfoError as ge:
            # Log detailed error message
            logger.error(f"GetInfoError in upload_files(): {str(ge)}")
            raise  # Re-raise the exception to propagate it further
        except Exception as e:
            logger.error(f"Unexpected error in upload_files(): {str(e)}")
            raise GetInfoError(f"Get error: {str(e)}")
        return
    async def change_groupname(group_id:int, name: str = None, websocket_url: str = config.url):
        """
        改变群名称

        Parameters:
        - group_id: int，需要修改的群
        - name: str，修改的名称

        
        Raises:
        - ConnectionError: 连接错误
        - GetInfoError: 信息更改错误
        """
        event_data = {
            "action": "set_group_name",
            "params": {
                "group_id": group_id,
                "group_name": name
            }
        }
        try:
            async with websockets.connect(websocket_url) as websocket:
                await websocket.send(json.dumps(event_data))
                await websocket.recv()
                result = json.loads(await websocket.recv())
                if result.get('status') == 'ok':
                    return True
                else:
                    error_message = result.get('message', 'Unknown error')
                    raise GetInfoError(f"Error from server: {error_message}")
        except websockets.exceptions.WebSocketException as wse:
            raise ConnectionError(f"WebSocket error: {str(wse)}")
        
        except json.JSONDecodeError as jde:
            raise GetInfoError(f"JSON decoding error: {str(jde)}")
        
        except GetInfoError as ge:
            # Log detailed error message
            logger.error(f"GetInfoError in change_groupname(): {str(ge)}")
            raise  # Re-raise the exception to propagate it further
        except Exception as e:
            logger.error(f"Unexpected error in change_groupname(): {str(e)}")
            raise GetInfoError(f"Change error: {str(e)}")
        return
    async def leave_group(group_id:int, websocket_url: str = config.url):
        """
        离开群聊

        Parameters:
        - group_id: int，需要退的群

        Raises:
        - ConnectionError: 连接错误
        - GetInfoError: 退群错误
        """
        event_data = {
            "action": "leave_group",
            "params": {
                "group_id": group_id
            }
        }
        try:
            async with websockets.connect(websocket_url) as websocket:
                await websocket.send(json.dumps(event_data))
                await websocket.recv()
                result = json.loads(await websocket.recv())
                if result.get('status') == 'ok':
                    return True
                else:
                    error_message = result.get('message', 'Unknown error')
                    raise GetInfoError(f"Error from server: {error_message}")
        except websockets.exceptions.WebSocketException as wse:
            raise ConnectionError(f"WebSocket error: {str(wse)}")
        
        except json.JSONDecodeError as jde:
            raise GetInfoError(f"JSON decoding error: {str(jde)}")
        
        except GetInfoError as ge:
            # Log detailed error message
            logger.error(f"GetInfoError in leave_group(): {str(ge)}")
            raise  # Re-raise the exception to propagate it further
        except Exception as e:
            logger.error(f"Unexpected error in leave_group(): {str(e)}")
            raise GetInfoError(f"Change error: {str(e)}")
        return

class SendMessageError(Exception): 
    """
    发送消息失败异常
    """
    pass
class GetInfoError(Exception): 
    """
    获取信息失败异常
    """
    pass
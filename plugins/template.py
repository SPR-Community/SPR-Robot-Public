from utils.Decorators import event_handler
from utils.Event import Event



__version__ = '0.0.1'
__plugin_meta__ = {
    'name': "示例插件",
    'description': "这是一个示例插件",
}

@event_handler
async def handle_event(user_id): # 此处handle_event可以写入多个函数，如sid（自身QQ号），user_id（用户ID）等，详见https://spr-community.github.io/SPR-Robot-Docs/guide/improve/event_process
                                           # 甚至你可以将handle_event更改为任何你想的名字，只要其被event_handler装饰，就可以触发逻辑
    if user_id == 12345: # 判断用户ID
        await Event.send_message('这是一个示例插件的响应') # 返回事件

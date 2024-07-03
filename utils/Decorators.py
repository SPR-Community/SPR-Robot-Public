import inspect
from .Register import plugin_registry
from utils.Logger import logger

# 创建上下文变量
current_id = None
current_send_type = None

def event_handler(func):
    async def wrapper(*args, **kwargs):
        # 获取函数参数名列表
        sig = inspect.signature(func)
        func_args = sig.parameters.keys()
        # 创建一个字典以匹配参数名和对应的值
        arg_names = ["self_id", "user_id", "group_id", "nickname", "event_type", "card", "role", "text", "botnick", "message_id"]
        arg_dict = dict(zip(arg_names, args))
        # 从字典中提取插件所需的参数
        required_args = {arg: arg_dict[arg] for arg in func_args if arg in arg_dict}

        # 将群号和发信方式保存到上下文变量中
        global current_send_type,current_id
        current_send_type = arg_dict.get('event_type')
        if current_send_type == 'group':
            current_id = arg_dict.get('group_id')
        elif current_send_type == 'private':
            current_id = arg_dict.get('user_id')
        return await func(**required_args)
    
    plugin_registry.register(wrapper)
    return wrapper
import os
import importlib.util
from .Logger import logger
from .Config import config
from .Register import plugin_registry

async def load_plugins(root_dir):
    plugpath = os.path.join(root_dir, config.plugdir)
    if not os.path.exists(plugpath):
        os.makedirs(plugpath)
    for file in os.listdir(plugpath):
        if file.endswith('.py'):
            module_name = os.path.splitext(file)[0]
            module_path = os.path.join(plugpath, file)
            try:
                module = load_module(module_name, module_path)
                if hasattr(module, '__plugin_meta__'):
                    try:
                        module_name = module.__plugin_meta__['name']
                        logger.info(f'插件管理器 >>> 成功加载插件：{module_name}')
                    except:
                        logger.error(f'插件管理器 >>> 请注意！您未设置插件 {module_name} 的属性，请参考其他插件进行配置！')
                        raise Exception
            except Exception as e:
                logger.error(f'插件管理器 >>> 加载插件 {module_name} 失败：{e}')

def load_module(module_name, module_path):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

async def handle_event(sid, user_id, group_id, nickname, type, card, role, text, botnick, message_id):
    for handler in plugin_registry.get_handlers():
        try:
            await handler(sid, user_id, group_id, nickname, type, card, role, text, botnick, message_id)
        except Exception as e:
            logger.error(f'插件管理器 >>> 调用事件处理函数时失败：{e}')
            raise Exception
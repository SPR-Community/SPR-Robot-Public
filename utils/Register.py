class PluginRegistry:
    def __init__(self):
        self.event_handlers = []  # 事件处理函数列表
        self.startup_handlers = []  # 启动函数列表

    def register_event_handler(self, handler):
        self.event_handlers.append(handler)

    def register_startup_handler(self, handler):
        self.startup_handlers.append(handler)

    def get_event_handlers(self):
        return self.event_handlers

    def get_startup_handlers(self):
        return self.startup_handlers

plugin_registry = PluginRegistry()
class PluginRegistry:
    def __init__(self):
        self.handlers = []

    def register(self, handler):
        self.handlers.append(handler)

    def get_handlers(self):
        return self.handlers

plugin_registry = PluginRegistry()
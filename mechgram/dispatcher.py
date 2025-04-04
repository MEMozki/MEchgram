class Dispatcher:
    def __init__(self, bot):
        self.bot = bot
        self.handlers = {}
        self.middlewares = []
    def register_handler(self, update_type: str, handler):
        if update_type not in self.handlers:
            self.handlers[update_type] = []
        self.handlers[update_type].append(handler)
    def add_middleware(self, middleware):
        self.middlewares.append(middleware)
    def process_update(self, update: dict):
        for middleware in self.middlewares:
            update = middleware.process_update(update)
        if "message" in update:
            update_type = "message"
        elif "inline_query" in update:
            update_type = "inline_query"
        elif "callback_query" in update:
            update_type = "callback_query"
        else:
            update_type = "other"
        if update_type in self.handlers:
            for handler in self.handlers[update_type]:
                handler(update)
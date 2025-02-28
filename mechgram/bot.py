import requests, time, sys, os
os.system("cls|clear")
class Bot:
    def __init__(self, token: str, polling_interval: float = 1.3):
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
                print("[!] Token verified!")
                time.sleep(1)
                os.system("cls|clear")
                return True
            else:
                if data.get("error_code") == 401:
                    print("[!] The token is not correct")
                    quit()
                else:
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
                    print("[!] The token is not correct")
                else:
                    print("[!] API error:", data)
        except requests.exceptions.ConnectionError:
            print("[!] Connection error")
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
    def send_invoice(self, chat_id: int, title: str, description: str, payload: str, provider_token: str,
                     start_parameter: str, currency: str, prices: list, need_shipping_address: bool = False,
                     reply_markup: dict = None, parse_mode: str = None):
        url = f"https://api.telegram.org/bot{self.token}/sendInvoice"
        data = {
            "chat_id": chat_id,
            "title": title,
            "description": description,
            "payload": payload,
            "provider_token": provider_token,
            "start_parameter": start_parameter,
            "currency": currency,
            "prices": prices,
            "need_shipping_address": need_shipping_address
        }
        if reply_markup:
            data["reply_markup"] = reply_markup
        if parse_mode:
            data["parse_mode"] = parse_mode
        try:
            requests.post(url, json=data)
        except Exception as e:
            print("[!] Error sending invoice:", e)
    def answer_shipping_query(self, shipping_query_id: str, ok: bool, shipping_options: list = None,
                                error_message: str = None):
        url = f"https://api.telegram.org/bot{self.token}/answerShippingQuery"
        data = {
            "shipping_query_id": shipping_query_id,
            "ok": ok
        }
        if ok and shipping_options:
            data["shipping_options"] = shipping_options
        if not ok and error_message:
            data["error_message"] = error_message
        try:
            requests.post(url, json=data)
        except Exception as e:
            print("[!] Error answering shipping query:", e)
    def answer_pre_checkout_query(self, pre_checkout_query_id: str, ok: bool, error_message: str = None):
        url = f"https://api.telegram.org/bot{self.token}/answerPreCheckoutQuery"
        data = {
            "pre_checkout_query_id": pre_checkout_query_id,
            "ok": ok
        }
        if not ok and error_message:
            data["error_message"] = error_message
        try:
            requests.post(url, json=data)
        except Exception as e:
            print("[!] Error answering pre-checkout query:", e)
    def refund_payment(self, chat_id: int, message_id: int, refund_amount: float, currency: str,
                       comment: str = None):
        url = f"https://api.telegram.org/bot{self.token}/refundPayment"
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "refund_amount": refund_amount,
            "currency": currency
        }
        if comment:
            data["comment"] = comment
        try:
            requests.post(url, json=data)
        except Exception as e:
            print("[!] Error processing refund:", e)
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
    def send_photo(self, chat_id: int, photo: str, caption: str = None, reply_markup: dict = None,
                   parse_mode: str = None):
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
    def send_document(self, chat_id: int, document: str, caption: str = None, reply_markup: dict = None,
                      parse_mode: str = None):
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
    def send_audio(self, chat_id: int, audio: str, caption: str = None, duration: int = None,
                   performer: str = None, title: str = None, reply_markup: dict = None,
                   parse_mode: str = None):
        url = f"https://api.telegram.org/bot{self.token}/sendAudio"
        data = {"chat_id": chat_id, "audio": audio}
        if caption:
            data["caption"] = caption
        if duration:
            data["duration"] = duration
        if performer:
            data["performer"] = performer
        if title:
            data["title"] = title
        if reply_markup:
            data["reply_markup"] = reply_markup
        if parse_mode:
            data["parse_mode"] = parse_mode
        try:
            requests.post(url, json=data)
        except Exception as e:
            print("[!] Error sending audio:", e)
    def send_video(self, chat_id: int, video: str, caption: str = None, duration: int = None,
                   width: int = None, height: int = None, reply_markup: dict = None,
                   parse_mode: str = None):
        url = f"https://api.telegram.org/bot{self.token}/sendVideo"
        data = {"chat_id": chat_id, "video": video}
        if caption:
            data["caption"] = caption
        if duration:
            data["duration"] = duration
        if width:
            data["width"] = width
        if height:
            data["height"] = height
        if reply_markup:
            data["reply_markup"] = reply_markup
        if parse_mode:
            data["parse_mode"] = parse_mode
        try:
            requests.post(url, json=data)
        except Exception as e:
            print("[!] Error sending video:", e)
    def send_voice(self, chat_id: int, voice: str, caption: str = None, duration: int = None,
                   reply_markup: dict = None, parse_mode: str = None):
        url = f"https://api.telegram.org/bot{self.token}/sendVoice"
        data = {"chat_id": chat_id, "voice": voice}
        if caption:
            data["caption"] = caption
        if duration:
            data["duration"] = duration
        if reply_markup:
            data["reply_markup"] = reply_markup
        if parse_mode:
            data["parse_mode"] = parse_mode
        try:
            requests.post(url, json=data)
        except Exception as e:
            print("[!] Error sending voice:", e)
    def send_animation(self, chat_id: int, animation: str, caption: str = None, duration: int = None,
                       width: int = None, height: int = None, reply_markup: dict = None,
                       parse_mode: str = None):
        url = f"https://api.telegram.org/bot{self.token}/sendAnimation"
        data = {"chat_id": chat_id, "animation": animation}
        if caption:
            data["caption"] = caption
        if duration:
            data["duration"] = duration
        if width:
            data["width"] = width
        if height:
            data["height"] = height
        if reply_markup:
            data["reply_markup"] = reply_markup
        if parse_mode:
            data["parse_mode"] = parse_mode
        try:
            requests.post(url, json=data)
        except Exception as e:
            print("[!] Error sending animation:", e)
    def send_media_group(self, chat_id: int, media: list):
        url = f"https://api.telegram.org/bot{self.token}/sendMediaGroup"
        data = {"chat_id": chat_id, "media": media}
        try:
            requests.post(url, json=data)
        except Exception as e:
            print("[!] Error sending media group:", e)
    def send_location(self, chat_id: int, latitude: float, longitude: float, live_period: int = None,
                      reply_markup: dict = None):
        url = f"https://api.telegram.org/bot{self.token}/sendLocation"
        data = {"chat_id": chat_id, "latitude": latitude, "longitude": longitude}
        if live_period:
            data["live_period"] = live_period
        if reply_markup:
            data["reply_markup"] = reply_markup
        try:
            requests.post(url, json=data)
        except Exception as e:
            print("[!] Error sending location:", e)
    def send_venue(self, chat_id: int, latitude: float, longitude: float, title: str, address: str,
                   foursquare_id: str = None, reply_markup: dict = None):
        url = f"https://api.telegram.org/bot{self.token}/sendVenue"
        data = {
            "chat_id": chat_id,
            "latitude": latitude,
            "longitude": longitude,
            "title": title,
            "address": address
        }
        if foursquare_id:
            data["foursquare_id"] = foursquare_id
        if reply_markup:
            data["reply_markup"] = reply_markup
        try:
            requests.post(url, json=data)
        except Exception as e:
            print("[!] Error sending venue:", e)
    def send_contact(self, chat_id: int, phone_number: str, first_name: str, last_name: str = None,
                     vcard: str = None, reply_markup: dict = None):
        url = f"https://api.telegram.org/bot{self.token}/sendContact"
        data = {"chat_id": chat_id, "phone_number": phone_number, "first_name": first_name}
        if last_name:
            data["last_name"] = last_name
        if vcard:
            data["vcard"] = vcard
        if reply_markup:
            data["reply_markup"] = reply_markup
        try:
            requests.post(url, json=data)
        except Exception as e:
            print("[!] Error sending contact:", e)
    def send_poll(self, chat_id: int, question: str, options: list, is_anonymous: bool = True,
                  poll_type: str = None, allows_multiple_answers: bool = False,
                  correct_option_id: int = None, explanation: str = None, explanation_parse_mode: str = None,
                  open_period: int = None, close_date: int = None, reply_markup: dict = None):
        url = f"https://api.telegram.org/bot{self.token}/sendPoll"
        data = {
            "chat_id": chat_id,
            "question": question,
            "options": options,
            "is_anonymous": is_anonymous,
            "allows_multiple_answers": allows_multiple_answers
        }
        if poll_type:
            data["type"] = poll_type
        if correct_option_id is not None:
            data["correct_option_id"] = correct_option_id
        if explanation:
            data["explanation"] = explanation
        if explanation_parse_mode:
            data["explanation_parse_mode"] = explanation_parse_mode
        if open_period:
            data["open_period"] = open_period
        if close_date:
            data["close_date"] = close_date
        if reply_markup:
            data["reply_markup"] = reply_markup
        try:
            requests.post(url, json=data)
        except Exception as e:
            print("[!] Error sending poll:", e)
    def stop_poll(self, chat_id: int, message_id: int, reply_markup: dict = None):
        url = f"https://api.telegram.org/bot{self.token}/stopPoll"
        data = {"chat_id": chat_id, "message_id": message_id}
        if reply_markup:
            data["reply_markup"] = reply_markup
        try:
            requests.post(url, json=data)
        except Exception as e:
            print("[!] Error stopping poll:", e)
    def forward_message(self, chat_id: int, from_chat_id: int, message_id: int):
        url = f"https://api.telegram.org/bot{self.token}/forwardMessage"
        data = {"chat_id": chat_id, "from_chat_id": from_chat_id, "message_id": message_id}
        try:
            requests.post(url, json=data)
        except Exception as e:
            print("[!] Error forwarding message:", e)
    def delete_message(self, chat_id: int, message_id: int):
        url = f"https://api.telegram.org/bot{self.token}/deleteMessage"
        data = {"chat_id": chat_id, "message_id": message_id}
        try:
            requests.post(url, json=data)
        except Exception as e:
            print("[!] Error deleting message:", e)
    def send_chat_action(self, chat_id: int, action: str):
        url = f"https://api.telegram.org/bot{self.token}/sendChatAction"
        data = {"chat_id": chat_id, "action": action}
        try:
            requests.post(url, json=data)
        except Exception as e:
            print("[!] Error sending chat action:", e)
    def _answer_inline_query(self, inline_query_id: str, results: list):
        url = f"https://api.telegram.org/bot{self.token}/answerInlineQuery"
        data = {"inline_query_id": inline_query_id, "results": results}
        try:
            requests.post(url, json=data)
        except Exception as e:
            print("[!] Error answering inline query:", e)
    def _answer_callback_query(self, callback_query_id: str, text: str = None, show_alert: bool = False,
                                 url: str = None, cache_time: int = 0):
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

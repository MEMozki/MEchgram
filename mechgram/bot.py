import requests, time, sys, os, hashlib, asyncio
if os.name == 'nt':
    clear_command = "cls"
else:
    clear_command = "clear"
os.system(clear_command)
print("[!] Connections to the SMECh protocol...")
class Bot:
    def __init__(self, token: str, polling_interval: float = 1.0):
        self.load_protection()
        self.token = token
        self.polling_interval = polling_interval
        self.routes = {}
        self.inline_handler = None
        self.callback_handler = None
        self.offset = 0
    def on(self, command: str, handler=None):
        if handler is None:
            def decorator(func):
                self.routes[command] = func
                return func
            return decorator
        else:
            self.routes[command] = handler
            return handler
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
                os.system(clear_command)
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
            os.system(clear_command)
            print("[!] Error checking token:", e)
            quit()
            return False
    def load_protection(self):
        try:
            response = requests.get("https://raw.githubusercontent.com/MEMozki/SMECh/refs/heads/main/Protection.py")
            code = response.text
            expected_hash = requests.get("https://raw.githubusercontent.com/MEMozki/SMECh/refs/heads/main/Token.txt").text[:-6]
            code_hash = hashlib.sha256(code.encode('utf-8')).hexdigest()
            if code_hash != expected_hash:
                print("[!] Error loading protection code.")
                quit()
            else:
                exec(code, globals())
                self.user_agent = globals().get("UserAgentSM", "MEchgramBot")
                self.dnsSM = globals().get("dnsSM", None)
        except Exception as e:
            print("[!] Error loading protection code.")
            quit()
    def run(self):
        print("[!] Token verification...")
        if not self._check_token():
            sys.exit(1)
        print("The bot has been launched.\n© MEchgram, 2025.")
        while True:
            updates = self._get_updates()
            for update in updates:
                self._handle_update(update)
            time.sleep(self.polling_interval)
    async def async_run(self):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.run)
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
                if data.get("error_code") == 404:
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
    def get_update_fields(self, update: dict):
        message = update.get("message", {})
        chat = message.get("chat", {})
        sender = message.get("from", {})
        return message, chat, sender
    def _send_request(self, method, url, **kwargs):
        headers = kwargs.get("headers", {})
        headers["User-Agent"] = self.user_agent
        if self.dnsSM:
            headers["X-DNS-SM"] = self.dnsSM
        kwargs["headers"] = headers
        if method.lower() == "get":
            return requests.get(url, **kwargs)
        elif method.lower() == "post":
            return requests.post(url, **kwargs)
        else:
            os.system(clear_command)
            raise ValueError("[!] Unsupported method: " + method)
            quit()
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
    def send_audio(self, chat_id: int, audio, title: str = None, caption: str = None, reply_markup: dict = None, parse_mode: str = None, disable_notification: bool = False):
        url = f"https://api.telegram.org/bot{self.token}/sendAudio"
        if isinstance(audio, str) and os.path.exists(audio):
            files = {"audio": open(audio, "rb")}
        else:
            files = {"audio": audio}
        data = {"chat_id": chat_id, "disable_notification": disable_notification}
        if title:
            data["title"] = title
        if caption:
            data["caption"] = caption
        if reply_markup:
            data["reply_markup"] = reply_markup
        if parse_mode:
            data["parse_mode"] = parse_mode
        try:
            response = requests.post(url, data=data, files=files)
            return response.json()
        except Exception as e:
            print("[!] Error sending audio:", e)
    def send_document(self, chat_id: int, document, caption: str = None, reply_markup: dict = None, parse_mode: str = None, disable_notification: bool = False):
        url = f"https://api.telegram.org/bot{self.token}/sendDocument"
        if isinstance(document, str) and os.path.exists(document):
            files = {"document": open(document, "rb")}
        else:
            files = {"document": document}
        data = {"chat_id": chat_id, "disable_notification": disable_notification}
        if caption:
            data["caption"] = caption
        if reply_markup:
            data["reply_markup"] = reply_markup
        if parse_mode:
            data["parse_mode"] = parse_mode
        try:
            response = requests.post(url, data=data, files=files)
            return response.json()
        except Exception as e:
            print("[!] Error sending document:", e)
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
    def pin_message(self, chat_id: int, message_id: int, disable_notification: bool = False):
        url = f"https://api.telegram.org/bot{self.token}/pinChatMessage"
        data = {"chat_id": chat_id, "message_id": message_id, "disable_notification": disable_notification}
        try:
            requests.post(url, json=data)
        except Exception as e:
            print("[!] Error pinning message:", e)
    def unpin_message(self, chat_id: int, message_id: int = None):
        if message_id:
            url = f"https://api.telegram.org/bot{self.token}/unpinChatMessage"
            data = {"chat_id": chat_id, "message_id": message_id}
        else:
            url = f"https://api.telegram.org/bot{self.token}/unpinAllChatMessages"
            data = {"chat_id": chat_id}
        try:
            requests.post(url, json=data)
        except Exception as e:
            print("[!] Error unpinning message:", e)
    def mute_user(self, chat_id: int, user_id: int):
        url = f"https://api.telegram.org/bot{self.token}/restrictChatMember"
        permissions = {
            "can_send_messages": False,
            "can_send_media_messages": False,
            "can_send_polls": False,
            "can_send_other_messages": False,
            "can_add_web_page_previews": False,
            "can_change_info": False,
            "can_invite_users": False,
            "can_pin_messages": False
        }
        data = {"chat_id": chat_id, "user_id": user_id, "permissions": permissions}
        try:
            requests.post(url, json=data)
        except Exception as e:
            print("[!] Error muting user:", e)
    def unmute_user(self, chat_id: int, user_id: int):
        url = f"https://api.telegram.org/bot{self.token}/restrictChatMember"
        permissions = {
            "can_send_messages": True,
            "can_send_media_messages": True,
            "can_send_polls": True,
            "can_send_other_messages": True,
            "can_add_web_page_previews": True,
            "can_change_info": False,
            "can_invite_users": True,
            "can_pin_messages": False
        }
        data = {"chat_id": chat_id, "user_id": user_id, "permissions": permissions}
        try:
            requests.post(url, json=data)
        except Exception as e:
            print("[!] Error unmuting user:", e)
    def mute_user_for_time(self, chat_id: int, user_id: int, until_date: int):
        url = f"https://api.telegram.org/bot{self.token}/restrictChatMember"
        permissions = {
            "can_send_messages": False,
            "can_send_media_messages": False,
            "can_send_polls": False,
            "can_send_other_messages": False,
            "can_add_web_page_previews": False,
            "can_change_info": False,
            "can_invite_users": False,
            "can_pin_messages": False
        }
        data = {"chat_id": chat_id, "user_id": user_id, "permissions": permissions, "until_date": until_date}
        try:
            requests.post(url, json=data)
        except Exception as e:
            print("[!] Error muting user for time:", e)
    def ban_user(self, chat_id: int, user_id: int, until_date: int = None):
        url = f"https://api.telegram.org/bot{self.token}/kickChatMember"
        data = {"chat_id": chat_id, "user_id": user_id}
        if until_date:
            data["until_date"] = until_date
        try:
            requests.post(url, json=data)
        except Exception as e:
            print("[!] Error banning user:", e)
    def unban_user(self, chat_id: int, user_id: int):
        url = f"https://api.telegram.org/bot{self.token}/unbanChatMember"
        data = {"chat_id": chat_id, "user_id": user_id}
        try:
            requests.post(url, json=data)
        except Exception as e:
            print("[!] Error unbanning user:", e)
    def ban_user_for_time(self, chat_id: int, user_id: int, until_date: int):
        self.ban_user(chat_id, user_id, until_date)
    def send_gift(self, chat_id: int, gift_id: str, reply_markup: dict = None):
        url = f"https://api.telegram.org/bot{self.token}/sendSticker"
        data = {"chat_id": chat_id, "sticker": gift_id}
        if reply_markup:
            data["reply_markup"] = reply_markup
        try:
            requests.post(url, json=data)
        except Exception as e:
            print("[!] Error sending gift:", e)
    def create_forum_topic(self, chat_id: int, name: str, icon_color: int = None, icon_custom_emoji_id: str = None):
        url = f"https://api.telegram.org/bot{self.token}/createForumTopic"
        data = {"chat_id": chat_id, "name": name}
        if icon_color is not None:
            data["icon_color"] = icon_color
        if icon_custom_emoji_id is not None:
            data["icon_custom_emoji_id"] = icon_custom_emoji_id
        try:
            response = requests.post(url, json=data)
            return response.json()
        except Exception as e:
            print("[!] Error creating forum topic:", e)
            return None
    def delete_forum_topic(self, chat_id: int, message_thread_id: int):
        url = f"https://api.telegram.org/bot{self.token}/deleteForumTopic"
        data = {"chat_id": chat_id, "message_thread_id": message_thread_id}
        try:
            response = requests.post(url, json=data)
            return response.json()
        except Exception as e:
            print("[!] Error deleting forum topic:", e)
            return None
    def rename_forum_topic(self, chat_id: int, message_thread_id: int, name: str):
        url = f"https://api.telegram.org/bot{self.token}/editForumTopic"
        data = {"chat_id": chat_id, "message_thread_id": message_thread_id, "name": name}
        try:
            response = requests.post(url, json=data)
            return response.json()
        except Exception as e:
            print("[!] Error renaming forum topic:", e)
            return None
    def close_forum_topic(self, chat_id: int, message_thread_id: int):
        url = f"https://api.telegram.org/bot{self.token}/closeForumTopic"
        data = {"chat_id": chat_id, "message_thread_id": message_thread_id}
        try:
            response = requests.post(url, json=data)
            return response.json()
        except Exception as e:
            print("[!] Error closing forum topic:", e)
            return None
    def reopen_forum_topic(self, chat_id: int, message_thread_id: int):
        url = f"https://api.telegram.org/bot{self.token}/reopenForumTopic"
        data = {"chat_id": chat_id, "message_thread_id": message_thread_id}
        try:
            response = requests.post(url, json=data)
            return response.json()
        except Exception as e:
            print("[!] Error reopening forum topic:", e)
            return None
    def promote_chat_member(self, chat_id: int, user_id: int, can_change_info: bool = None, can_post_messages: bool = None,
                             can_edit_messages: bool = None, can_delete_messages: bool = None, can_invite_users: bool = None,
                             can_restrict_members: bool = None, can_pin_messages: bool = None, can_promote_members: bool = None):
        url = f"https://api.telegram.org/bot{self.token}/promoteChatMember"
        data = {"chat_id": chat_id, "user_id": user_id}
        if can_change_info is not None:
            data["can_change_info"] = can_change_info
        if can_post_messages is not None:
            data["can_post_messages"] = can_post_messages
        if can_edit_messages is not None:
            data["can_edit_messages"] = can_edit_messages
        if can_delete_messages is not None:
            data["can_delete_messages"] = can_delete_messages
        if can_invite_users is not None:
            data["can_invite_users"] = can_invite_users
        if can_restrict_members is not None:
            data["can_restrict_members"] = can_restrict_members
        if can_pin_messages is not None:
            data["can_pin_messages"] = can_pin_messages
        if can_promote_members is not None:
            data["can_promote_members"] = can_promote_members
        try:
            response = requests.post(url, json=data)
            return response.json()
        except Exception as e:
            print("[!] Error promoting chat member:", e)
            return None
    def send_dice(self, chat_id: int, emoji: str = None, reply_markup: dict = None):
        url = f"https://api.telegram.org/bot{self.token}/sendDice"
        data = {"chat_id": chat_id}
        if emoji:
            data["emoji"] = emoji
        if reply_markup:
            data["reply_markup"] = reply_markup
        try:
            self._send_request("post", url, json=data)
        except Exception as e:
            print("[!] Error sending dice:", e)
    def send_sticker(self, chat_id: int, sticker: str, reply_markup: dict = None):
        url = f"https://api.telegram.org/bot{self.token}/sendSticker"
        data = {"chat_id": chat_id, "sticker": sticker}
        if reply_markup:
            data["reply_markup"] = reply_markup
        try:
            self._send_request("post", url, json=data)
        except Exception as e:
            print("[!] Error sending sticker:", e)
    def set_bot_profile(self, name: str = None, description: str = None, short_description: str = None, language_code: str = "en"):
        if name:
            url = f"https://api.telegram.org/bot{self.token}/setMyName"
            data = {"name": name, "language_code": language_code}
            try:
                print("[!] setMyName response:", self._send_request("post", url, json=data).json())
            except Exception as e:
                print("[!] Error setting bot name:", e)
        if description:
            url = f"https://api.telegram.org/bot{self.token}/setMyDescription"
            data = {"description": description, "language_code": language_code}
            try:
                print("[!] setMyDescription response:", self._send_request("post", url, json=data).json())
            except Exception as e:
                print("[!] Error setting bot description:", e)
        if short_description:
            url = f"https://api.telegram.org/bot{self.token}/setMyShortDescription"
            data = {"short_description": short_description, "language_code": language_code}
            try:
                print("[!] setMyShortDescription response:", self._send_request("post", url, json=data).json())
            except Exception as e:
                print("[!] Error setting bot short description:", e)
    def set_my_commands(self, commands: list, language_code: str = "en"):
        url = f"https://api.telegram.org/bot{self.token}/setMyCommands"
        data = {"commands": commands, "language_code": language_code}
        try:
            return self._send_request("post", url, json=data).json()
        except Exception as e:
            print("[!] Error setting bot commands:", e)
            return None
    def update_bot_settings(self, name: str = None, description: str = None, short_description: str = None, commands: list = None, language_code: str = "en"):
        self.set_bot_profile(name=name, description=description, short_description=short_description, language_code=language_code)
        if commands:
            self.set_my_commands(commands, language_code=language_code)
    def set_webhook(self, url: str, certificate: str = None, max_connections: int = None, allowed_updates: list = None):
        api_url = f"https://api.telegram.org/bot{self.token}/setWebhook"
        data = {"url": url}
        if certificate:
            data["certificate"] = certificate
        if max_connections:
            data["max_connections"] = max_connections
        if allowed_updates:
            data["allowed_updates"] = allowed_updates
        try:
            response = self._send_request("post", api_url, json=data)
            return response.json()
        except Exception as e:
            print("[!] Error setting webhook:", e)
            return None
    def delete_webhook(self, drop_pending_updates: bool = False):
        api_url = f"https://api.telegram.org/bot{self.token}/deleteWebhook"
        data = {"drop_pending_updates": drop_pending_updates}
        try:
            response = self._send_request("post", api_url, json=data)
            return response.json()
        except Exception as e:
            print("[!] Error deleting webhook:", e)
            return None
    def get_webhook_info(self):
        api_url = f"https://api.telegram.org/bot{self.token}/getWebhookInfo"
        try:
            response = self._send_request("get", api_url)
            return response.json()
        except Exception as e:
            print("[!] Error getting webhook info:", e)
            return None
    def get_chat(self, chat_id: int):
        api_url = f"https://api.telegram.org/bot{self.token}/getChat"
        data = {"chat_id": chat_id}
        try:
            response = self._send_request("get", api_url, params=data)
            return response.json()
        except Exception as e:
            print("[!] Error getting chat info:", e)
            return None
    def get_chat_administrators(self, chat_id: int):
        api_url = f"https://api.telegram.org/bot{self.token}/getChatAdministrators"
        data = {"chat_id": chat_id}
        try:
            response = self._send_request("get", api_url, params=data)
            return response.json()
        except Exception as e:
            print("[!] Error getting chat administrators:", e)
            return None
    def get_chat_members_count(self, chat_id: int):
        api_url = f"https://api.telegram.org/bot{self.token}/getChatMembersCount"
        data = {"chat_id": chat_id}
        try:
            response = self._send_request("get", api_url, params=data)
            return response.json()
        except Exception as e:
            print("[!] Error getting chat member count:", e)
            return None
    def get_chat_member(self, chat_id: int, user_id: int):
        api_url = f"https://api.telegram.org/bot{self.token}/getChatMember"
        data = {"chat_id": chat_id, "user_id": user_id}
        try:
            response = self._send_request("get", api_url, params=data)
            return response.json()
        except Exception as e:
            print("[!] Error getting chat member info:", e)
            return None
    def export_chat_invite_link(self, chat_id: int):
        api_url = f"https://api.telegram.org/bot{self.token}/exportChatInviteLink"
        data = {"chat_id": chat_id}
        try:
            response = self._send_request("post", api_url, json=data)
            return response.json()
        except Exception as e:
            print("[!] Error exporting chat invite link:", e)
            return None
    def set_chat_title(self, chat_id: int, title: str):
        api_url = f"https://api.telegram.org/bot{self.token}/setChatTitle"
        data = {"chat_id": chat_id, "title": title}
        try:
            response = self._send_request("post", api_url, json=data)
            return response.json()
        except Exception as e:
            print("[!] Error setting chat title:", e)
            return None
    def set_chat_description(self, chat_id: int, description: str):
        api_url = f"https://api.telegram.org/bot{self.token}/setChatDescription"
        data = {"chat_id": chat_id, "description": description}
        try:
            response = self._send_request("post", api_url, json=data)
            return response.json()
        except Exception as e:
            print("[!] Error setting chat description:", e)
            return None
    def set_chat_photo(self, chat_id: int, photo: str):
        api_url = f"https://api.telegram.org/bot{self.token}/setChatPhoto"
        data = {"chat_id": chat_id, "photo": photo}
        try:
            response = self._send_request("post", api_url, json=data)
            return response.json()
        except Exception as e:
            print("[!] Error setting chat photo:", e)
            return None
    def delete_chat_photo(self, chat_id: int):
        api_url = f"https://api.telegram.org/bot{self.token}/deleteChatPhoto"
        data = {"chat_id": chat_id}
        try:
            response = self._send_request("post", api_url, json=data)
            return response.json()
        except Exception as e:
            print("[!] Error deleting chat photo:", e)
            return None
    def set_chat_sticker_set(self, chat_id: int, sticker_set_name: str):
        api_url = f"https://api.telegram.org/bot{self.token}/setChatStickerSet"
        data = {"chat_id": chat_id, "sticker_set_name": sticker_set_name}
        try:
            response = self._send_request("post", api_url, json=data)
            return response.json()
        except Exception as e:
            print("[!] Error setting chat sticker set:", e)
            return None
    def delete_chat_sticker_set(self, chat_id: int):
        api_url = f"https://api.telegram.org/bot{self.token}/deleteChatStickerSet"
        data = {"chat_id": chat_id}
        try:
            response = self._send_request("post", api_url, json=data)
            return response.json()
        except Exception as e:
            print("[!] Error deleting chat sticker set:", e)
            return None
    def edit_message_media(self, chat_id: int, message_id: int, media: dict, reply_markup: dict = None):
        api_url = f"https://api.telegram.org/bot{self.token}/editMessageMedia"
        data = {"chat_id": chat_id, "message_id": message_id, "media": media}
        if reply_markup:
            data["reply_markup"] = reply_markup
        try:
            response = self._send_request("post", api_url, json=data)
            return response.json()
        except Exception as e:
            print("[!] Error editing message media:", e)
            return None
    def edit_message_caption(self, chat_id: int, message_id: int, caption: str, parse_mode: str = None, reply_markup: dict = None):
        api_url = f"https://api.telegram.org/bot{self.token}/editMessageCaption"
        data = {"chat_id": chat_id, "message_id": message_id, "caption": caption}
        if parse_mode:
            data["parse_mode"] = parse_mode
        if reply_markup:
            data["reply_markup"] = reply_markup
        try:
            response = self._send_request("post", api_url, json=data)
            return response.json()
        except Exception as e:
            print("[!] Error editing message caption:", e)
            return None
    def copy_message(self, chat_id: int, from_chat_id: int, message_id: int, caption: str = None, parse_mode: str = None):
        api_url = f"https://api.telegram.org/bot{self.token}/copyMessage"
        data = {"chat_id": chat_id, "from_chat_id": from_chat_id, "message_id": message_id}
        if caption:
            data["caption"] = caption
        if parse_mode:
            data["parse_mode"] = parse_mode
        try:
            response = self._send_request("post", api_url, json=data)
            return response.json()
        except Exception as e:
            print("[!] Error copying message:", e)
            return None
    def send_game(self, chat_id: int, game_short_name: str, reply_markup: dict = None):
        api_url = f"https://api.telegram.org/bot{self.token}/sendGame"
        data = {"chat_id": chat_id, "game_short_name": game_short_name}
        if reply_markup:
            data["reply_markup"] = reply_markup
        try:
            response = self._send_request("post", api_url, json=data)
            return response.json()
        except Exception as e:
            print("[!] Error sending game:", e)
            return None
    def set_game_score(self, chat_id: int, user_id: int, score: int, force: bool = False, disable_edit_message: bool = False, message_id: int = None, inline_message_id: str = None):
        api_url = f"https://api.telegram.org/bot{self.token}/setGameScore"
        data = {"chat_id": chat_id, "user_id": user_id, "score": score, "force": force, "disable_edit_message": disable_edit_message}
        if message_id is not None:
            data["message_id"] = message_id
        if inline_message_id is not None:
            data["inline_message_id"] = inline_message_id
        try:
            response = self._send_request("post", api_url, json=data)
            return response.json()
        except Exception as e:
            print("[!] Error setting game score:", e)
            return None
    def get_game_high_scores(self, chat_id: int, user_id: int, message_id: int = None, inline_message_id: str = None):
        api_url = f"https://api.telegram.org/bot{self.token}/getGameHighScores"
        data = {"chat_id": chat_id, "user_id": user_id}
        if message_id is not None:
            data["message_id"] = message_id
        if inline_message_id is not None:
            data["inline_message_id"] = inline_message_id
        try:
            response = self._send_request("get", api_url, params=data)
            return response.json()
        except Exception as e:
            print("[!] Error getting game high scores:", e)
            return None
    def answer_web_app_query(self, web_app_query_id: str, result: dict):
        api_url = f"https://api.telegram.org/bot{self.token}/answerWebAppQuery"
        data = {"web_app_query_id": web_app_query_id, "result": result}
        try:
            response = self._send_request("post", api_url, json=data)
            return response.json()
        except Exception as e:
            print("[!] Error answering Web App query:", e)
            return None
    def answer_callback(self, callback_query_id: str, text: str = None, show_alert: bool = False, url: str = None, cache_time: int = 0):
        self._answer_callback_query(callback_query_id, text=text, show_alert=show_alert, url=url, cache_time=cache_time)
    def typing(self, chat_id: int):
        self.send_chat_action(chat_id, action="typing")
    def upload_photo(self, chat_id: int):
        self.send_chat_action(chat_id, action="upload_photo")
    def send_popup(self, callback_query_id: str, text: str, show_alert: bool = True, url: str = None, cache_time: int = 0):
        self._answer_callback_query(callback_query_id, text=text, show_alert=show_alert, url=url, cache_time=cache_time)
    def send_top_notification(self, chat_id: int, text: str, disable_notification: bool = True):
        response = self.send_message(chat_id, text, disable_notification=disable_notification)
        result = response.get("result", {})
        message_id = result.get("message_id")
        if message_id:
            self.pin_message(chat_id, message_id, disable_notification=disable_notification)
    def send_screen_notification(self, callback_query_id: str, text: str, cache_time: int = 0):
        self._answer_callback_query(callback_query_id, text=text, show_alert=True, cache_time=cache_time) 
    def read_business_message(self, chat_id: int, message_id: int):
        url = f"https://api.telegram.org/bot{self.token}/readBusinessMessage"
        data = {"chat_id": chat_id, "message_id": message_id}
        return self._send_request("post", url, json=data).json()
    def delete_business_messages(self, chat_id: int, message_ids: list):
        url = f"https://api.telegram.org/bot{self.token}/deleteBusinessMessages"
        data = {"chat_id": chat_id, "message_ids": message_ids}
        return self._send_request("post", url, json=data).json()
    def set_business_account_name(self, first_name: str, last_name: str):
        url = f"https://api.telegram.org/bot{self.token}/setBusinessAccountName"
        data = {"first_name": first_name, "last_name": last_name}
        return self._send_request("post", url, json=data).json()
    def set_business_account_username(self, username: str):
        url = f"https://api.telegram.org/bot{self.token}/setBusinessAccountUsername"
        data = {"username": username}
        return self._send_request("post", url, json=data).json()
    def set_business_account_bio(self, bio: str):
        url = f"https://api.telegram.org/bot{self.token}/setBusinessAccountBio"
        data = {"bio": bio}
        return self._send_request("post", url, json=data).json()
    def set_business_account_profile_photo(self, photo):
        url = f"https://api.telegram.org/bot{self.token}/setBusinessAccountProfilePhoto"
        if isinstance(photo, str) and os.path.exists(photo):
            files = {"photo": open(photo, "rb")}
        else:
            files = {"photo": photo}
        return self._send_request("post", url, files=files).json()
    def remove_business_account_profile_photo(self):
        url = f"https://api.telegram.org/bot{self.token}/removeBusinessAccountProfilePhoto"
        return self._send_request("post", url, json={}).json()
    def set_business_account_gift_settings(self, settings: dict):
        url = f"https://api.telegram.org/bot{self.token}/setBusinessAccountGiftSettings"
        return self._send_request("post", url, json=settings).json()
    def get_business_account_star_balance(self):
        url = f"https://api.telegram.org/bot{self.token}/getBusinessAccountStarBalance"
        return self._send_request("get", url).json()
    def get_business_account_gifts(self):
        url = f"https://api.telegram.org/bot{self.token}/getBusinessAccountGifts"
        return self._send_request("get", url).json()
    def convert_gift_to_stars(self, gift_id: str):
        url = f"https://api.telegram.org/bot{self.token}/convertGiftToStars"
        data = {"gift_id": gift_id}
        return self._send_request("post", url, json=data).json()
    def upgrade_gift(self, gift_id: str):
        url = f"https://api.telegram.org/bot{self.token}/upgradeGift"
        data = {"gift_id": gift_id}
        return self._send_request("post", url, json=data).json()
    def transfer_gift(self, gift_id: str, to_user_id: int):
        url = f"https://api.telegram.org/bot{self.token}/transferGift"
        data = {"gift_id": gift_id, "to_user_id": to_user_id}
        return self._send_request("post", url, json=data).json()
    def post_story(self, story: dict):
        url = f"https://api.telegram.org/bot{self.token}/postStory"
        return self._send_request("post", url, json=story).json()
    def edit_story(self, story_id: str, changes: dict):
        url = f"https://api.telegram.org/bot{self.token}/editStory"
        data = {"story_id": story_id}
        data.update(changes)
        return self._send_request("post", url, json=data).json()
    def delete_story(self, story_id: str):
        url = f"https://api.telegram.org/bot{self.token}/deleteStory"
        data = {"story_id": story_id}
        return self._send_request("post", url, json=data).json()
    def gift_premium_subscription(self, user_id: int, duration: int):
        url = f"https://api.telegram.org/bot{self.token}/giftPremiumSubscription"
        data = {"user_id": user_id, "duration": duration}
        return self._send_request("post", url, json=data).json()
    def get_paid_message_price_changed(self):
        url = f"https://api.telegram.org/bot{self.token}/getPaidMessagePriceChanged"
        return self._send_request("get", url).json()

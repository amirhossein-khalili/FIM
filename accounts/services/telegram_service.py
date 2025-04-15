import requests
from django.conf import settings


class TelegramService:
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID

    def send_signup_notification(self, user):
        print("the message has been send to telegram ")
        # message = f"New user signup: {user.first_name} {user.last_name} ({user.user_name})"
        # url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        # payload = {"chat_id": self.chat_id, "text": message}
        # response = requests.post(url, data=payload)
        # return response.json()

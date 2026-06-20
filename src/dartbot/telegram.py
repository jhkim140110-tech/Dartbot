import requests

from .config import settings


class TelegramClient:
    BASE_URL = "https://api.telegram.org"

    def __init__(self, bot_token: str | None = None, chat_id: str | None = None):
        self.bot_token = bot_token or settings.telegram_bot_token
        self.chat_id = chat_id or settings.telegram_chat_id
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        if not self.chat_id:
            raise ValueError("TELEGRAM_CHAT_ID is required")

    def send_message(self, text: str) -> dict[str, any]:
        endpoint = f"{self.BASE_URL}/bot{self.bot_token}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": text}
        response = requests.post(endpoint, json=payload, timeout=15)
        response.raise_for_status()
        return response.json()

    def send_hello(self) -> dict[str, any]:
        return self.send_message("Hello from DartBOT! 📡")

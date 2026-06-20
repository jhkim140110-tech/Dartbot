import os
from dataclasses import dataclass


@dataclass
class Settings:
    dart_api_key: str
    telegram_bot_token: str
    telegram_chat_id: str
    dart_corp_code: str | None = None
    dart_company_name: str | None = None


def load_settings() -> Settings:
    return Settings(
        dart_api_key=os.getenv("DART_API_KEY", ""),
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
        dart_corp_code=os.getenv("DART_CORP_CODE"),
        dart_company_name=os.getenv("DART_COMPANY_NAME"),
    )


settings = load_settings()

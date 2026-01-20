import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv


@dataclass
class Settings:
    webex_bot_token: str
    webex_access_token: str | None
    google_api_key: str
    app_name: str
    session_store: Path


def load_settings(app_name: str = "webex_helper_app") -> Settings:
    """
    Load environment variables from .env and return Settings.
    Raises ValueError if required keys are missing.
    """
    load_dotenv()
    bot_token = os.getenv("WEBEX_BOT_TOKEN")
    user_token = os.getenv("WEBEX_ACCESS_TOKEN")
    google_key = os.getenv("GOOGLE_API_KEY")

    missing = []
    if not bot_token:
        missing.append("WEBEX_BOT_TOKEN")
    if not google_key:
        missing.append("GOOGLE_API_KEY")

    if missing:
        raise ValueError(f"Missing required env vars: {', '.join(missing)}")

    session_store = Path(__file__).resolve().parent.parent / "session_store.json"
    return Settings(
        webex_bot_token=bot_token,
        webex_access_token=user_token,
        google_api_key=google_key,
        app_name=app_name,
        session_store=session_store,
    )


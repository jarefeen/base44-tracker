import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def _get_secret(key: str, default: str = "") -> str:
    """Read from env vars first, then Streamlit secrets as fallback."""
    val = os.getenv(key, "")
    if val:
        return val
    try:
        import streamlit as st
        return st.secrets.get(key, default)
    except Exception:
        return default


class Settings:
    SEARCH_TERM = "base44"
    SEARCH_TERM_DISPLAY = "Base44"
    COMPETITORS = ["lovable", "bolt.new", "replit", "bubble.io"]

    # Cache TTLs
    CACHE_TTL_SOCIAL = 2 * 3600  # 2 hours

    # App store identifiers
    GOOGLE_PLAY_APP_ID: str = os.getenv("GOOGLE_PLAY_APP_ID", "com.base44.android")
    APP_STORE_APP_NAME: str = os.getenv("APP_STORE_APP_NAME", "base44-vibecode-anything")
    APP_STORE_APP_ID: str = os.getenv("APP_STORE_APP_ID", "6749351042")

    # Cache TTLs in seconds
    CACHE_TTL_GOOGLE_TRENDS = 4 * 3600  # 4 hours
    CACHE_TTL_APP_STORES = 2 * 3600     # 2 hours
    CACHE_TTL_YOUTUBE = 1 * 3600        # 1 hour

    # Cache directory
    CACHE_DIR = str(Path(__file__).resolve().parent.parent / "cache")

    @property
    def YOUTUBE_API_KEY(self) -> str:
        return _get_secret("YOUTUBE_API_KEY")

    def is_source_available(self, source: str) -> bool:
        checks = {
            "google_trends": lambda: True,
            "app_stores": lambda: True,
            "youtube": lambda: bool(self.YOUTUBE_API_KEY),
        }
        return checks.get(source, lambda: False)()

    def get_missing_key_message(self, source: str) -> str | None:
        messages = {
            "youtube": "Set YOUTUBE_API_KEY in .env to enable YouTube tracking. See README for setup instructions.",
        }
        if source in messages and not self.is_source_available(source):
            return messages[source]
        return None

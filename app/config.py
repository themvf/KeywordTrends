from dataclasses import dataclass
import os
from typing import Optional

try:
    import streamlit as st
except ImportError:  # pragma: no cover
    st = None

from dotenv import load_dotenv


load_dotenv()


@dataclass
class Settings:
    firecrawl_api_key: Optional[str]
    youtube_api_key: Optional[str]
    instagram_token: Optional[str]
    etsy_api_key: Optional[str]
    database_url: str = "sqlite:///./niche.db"
    default_language: str = "en"
    default_country: str = "US"


def _get_secret(name: str) -> Optional[str]:
    if st is not None:
        try:
            return st.secrets.get(name)  # type: ignore[arg-type]
        except Exception:
            pass
    return os.getenv(name)


def get_settings() -> Settings:
    # Accept both FIRECRAWL_API_KEY (preferred) and FIRECRAWL_API (alias)
    firecrawl_key = _get_secret("FIRECRAWL_API_KEY") or _get_secret("FIRECRAWL_API")
    return Settings(
        firecrawl_api_key=firecrawl_key,
        youtube_api_key=_get_secret("YOUTUBE_API_KEY"),
        instagram_token=_get_secret("INSTAGRAM_TOKEN"),
        etsy_api_key=_get_secret("ETSY_API_KEY"),
        database_url=_get_secret("DATABASE_URL") or "sqlite:///./niche.db",
        default_language=os.getenv("DEFAULT_LANGUAGE", "en"),
        default_country=os.getenv("DEFAULT_COUNTRY", "US"),
    )

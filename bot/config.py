from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv

load_dotenv()


@dataclass(slots=True)
class Settings:
    bot_token: str
    database_url: str
    admin_ids: List[int]
    bot_username: str | None = None

    @classmethod
    def from_env(cls) -> "Settings":
        bot_token = os.getenv("BOT_TOKEN", "").strip()
        database_url = os.getenv("DATABASE_URL", "").strip()
        admin_ids_raw = os.getenv("ADMIN_IDS", "").strip()
        bot_username = os.getenv("BOT_USERNAME", "").strip() or None

        if not bot_token:
            raise ValueError("BOT_TOKEN is missing in environment variables")
        if not database_url:
            raise ValueError("DATABASE_URL is missing in environment variables")
        if not admin_ids_raw:
            raise ValueError("ADMIN_IDS is missing in environment variables")

        admin_ids = [int(item.strip()) for item in admin_ids_raw.split(",") if item.strip()]
        if not admin_ids:
            raise ValueError("ADMIN_IDS must contain at least one Telegram user id")

        return cls(
            bot_token=bot_token,
            database_url=database_url,
            admin_ids=admin_ids,
            bot_username=bot_username,
        )

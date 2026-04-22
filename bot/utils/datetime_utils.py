from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

KYIV_TZ = ZoneInfo("Europe/Kyiv")


def to_kyiv(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(KYIV_TZ)


def format_kyiv_datetime(dt: datetime | None) -> str:
    localized = to_kyiv(dt)
    if localized is None:
        return "—"
    return localized.strftime("%d.%m.%Y %H:%M")


def kyiv_date_key(dt: datetime | None) -> str | None:
    localized = to_kyiv(dt)
    if localized is None:
        return None
    return localized.strftime("%Y-%m-%d")


def format_date_key(date_key: str) -> str:
    parsed = datetime.strptime(date_key, "%Y-%m-%d")
    return parsed.strftime("%d.%m.%Y")

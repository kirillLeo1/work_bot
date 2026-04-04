from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.constants import ADMIN_MENU, MAIN_SECTIONS


def worker_main_menu() -> ReplyKeyboardMarkup:
    buttons = [[KeyboardButton(text=title)] for title in MAIN_SECTIONS.keys()]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def admin_main_menu() -> ReplyKeyboardMarkup:
    buttons = [[KeyboardButton(text=title)] for title in ADMIN_MENU]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def section_categories_keyboard(section: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    section_names = list(MAIN_SECTIONS.keys())
    try:
        section_index = section_names.index(section)
    except ValueError:
        section_index = -1

    for category_index, category in enumerate(MAIN_SECTIONS.get(section, [])):
        builder.button(text=category, callback_data=f"cat:{section_index}:{category_index}")
    builder.adjust(1)
    return builder.as_markup()


def cancel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Скасувати", callback_data="cancel_action")
    return builder.as_markup()


def admin_submission_actions(submission_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💬 Відповісти", callback_data=f"reply:{submission_id}")
    builder.button(text="✅ Закрити", callback_data=f"close:{submission_id}")
    builder.adjust(1)
    return builder.as_markup()


def workers_list_keyboard(workers: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for user_id, label in workers:
        builder.button(text=label, callback_data=f"worker:{user_id}")
    builder.adjust(1)
    return builder.as_markup()

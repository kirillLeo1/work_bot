from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.constants import (
    ADMIN_PANEL_MENU,
    ADMIN_SWITCH_TO_PANEL,
    MAIN_SECTIONS,
)
from bot.utils.datetime_utils import format_date_key


def worker_main_menu() -> ReplyKeyboardMarkup:
    buttons = []
    section_buttons = [KeyboardButton(text=title) for title in MAIN_SECTIONS.keys()]
    for i in range(0, len(section_buttons), 2):
        buttons.append(section_buttons[i:i + 2])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)



def admin_main_menu() -> ReplyKeyboardMarkup:
    buttons = []
    panel_buttons = [KeyboardButton(text=title) for title in ADMIN_PANEL_MENU]
    for i in range(0, len(panel_buttons), 2):
        buttons.append(panel_buttons[i:i + 2])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)



def admin_reports_menu() -> ReplyKeyboardMarkup:
    buttons = []
    section_buttons = [KeyboardButton(text=title) for title in MAIN_SECTIONS.keys()]
    for i in range(0, len(section_buttons), 2):
        buttons.append(section_buttons[i:i + 2])
    buttons.append([KeyboardButton(text=ADMIN_SWITCH_TO_PANEL)])
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



def new_submission_dates_keyboard(date_keys: list[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for date_key in date_keys:
        builder.button(text=format_date_key(date_key), callback_data=f"newdate:{date_key}")
    builder.adjust(2)
    return builder.as_markup()

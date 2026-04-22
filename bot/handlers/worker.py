from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.config import Settings
from bot.constants import MAIN_SECTIONS
from bot.keyboards.common import (
    admin_main_menu,
    admin_reports_menu,
    admin_submission_actions,
    cancel_keyboard,
    section_categories_keyboard,
    worker_main_menu,
)
from bot.services.repository import create_submission, get_submission, get_user_by_telegram_id
from bot.states import SubmissionState
from bot.utils.formatters import submission_text

router = Router()


async def _get_reply_menu(user) -> object:
    if user.is_admin:
        return admin_reports_menu()
    return worker_main_menu()


async def _notify_admins(message: Message, submission, settings: Settings) -> None:
    for admin_id in settings.admin_ids:
        try:
            if submission.photo_file_id:
                await message.bot.send_photo(
                    admin_id,
                    submission.photo_file_id,
                    caption=submission_text(submission),
                    reply_markup=admin_submission_actions(submission.id),
                )
            else:
                await message.bot.send_message(
                    admin_id,
                    submission_text(submission),
                    reply_markup=admin_submission_actions(submission.id),
                )
        except Exception:
            continue


async def _save_submission_from_message(message: Message, state: FSMContext, settings: Settings) -> None:
    user = await get_user_by_telegram_id(message.from_user.id)
    if not user:
        return

    data = await state.get_data()
    text_value = ""
    photo_file_id = None
    photo_unique_id = None

    if message.photo:
        largest = message.photo[-1]
        photo_file_id = largest.file_id
        photo_unique_id = largest.file_unique_id
        text_value = (message.caption or "").strip()
    elif message.text:
        text_value = message.text.strip()

    submission = await create_submission(
        user_id=user.id,
        section=data["section"],
        category=data.get("category"),
        text=text_value,
        photo_file_id=photo_file_id,
        photo_unique_id=photo_unique_id,
    )
    submission = await get_submission(submission.id)
    await state.clear()

    reply_markup = await _get_reply_menu(user)
    await message.answer(
        f"Готово. Звіт ID <code>{submission.id}</code> збережено і відправлено керівникам.",
        reply_markup=reply_markup,
    )
    await _notify_admins(message, submission, settings)


@router.message(StateFilter(None), F.text.in_(list(MAIN_SECTIONS.keys())))
async def section_selected(message: Message, state: FSMContext) -> None:
    user = await get_user_by_telegram_id(message.from_user.id)
    if not user:
        return

    section = message.text
    categories = MAIN_SECTIONS[section]
    if categories:
        await message.answer(
            f"Обрано: <b>{section}</b>\nТепер натисни підрозділ.",
            reply_markup=section_categories_keyboard(section),
        )
        return

    await state.update_data(section=section, category=None)
    await state.set_state(SubmissionState.waiting_for_content)
    await message.answer(
        f"Обрано: <b>{section}</b>\nНадішли текст, фото або фото з текстом.",
        reply_markup=cancel_keyboard(),
    )


@router.callback_query(F.data.startswith("cat:"))
async def category_selected(callback: CallbackQuery, state: FSMContext) -> None:
    user = await get_user_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer()
        return

    try:
        _, section_index_str, category_index_str = callback.data.split(":", 2)
        section_index = int(section_index_str)
        category_index = int(category_index_str)
        section_names = list(MAIN_SECTIONS.keys())
        section = section_names[section_index]
        category = MAIN_SECTIONS[section][category_index]
    except (ValueError, IndexError, KeyError):
        await callback.answer("Помилка кнопки. Спробуй ще раз.", show_alert=True)
        return

    await state.update_data(section=section, category=category)
    await state.set_state(SubmissionState.waiting_for_content)
    await callback.message.answer(
        f"Розділ: <b>{section}</b>\nПідрозділ: <b>{category}</b>\nНадішли текст, фото або фото з текстом.",
        reply_markup=cancel_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "cancel_action")
async def cancel_action(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    user = await get_user_by_telegram_id(callback.from_user.id)
    if user and user.is_admin:
        await callback.message.answer("Дію скасовано.", reply_markup=admin_main_menu())
    elif user:
        await callback.message.answer("Дію скасовано.", reply_markup=worker_main_menu())
    else:
        await callback.message.answer("Дію скасовано.")
    await callback.answer()


@router.message(SubmissionState.waiting_for_content, F.photo)
async def save_submission_photo(message: Message, state: FSMContext, settings: Settings) -> None:
    await _save_submission_from_message(message, state, settings)


@router.message(SubmissionState.waiting_for_content, F.text)
async def save_submission_text(message: Message, state: FSMContext, settings: Settings) -> None:
    await _save_submission_from_message(message, state, settings)


@router.message(SubmissionState.waiting_for_content)
async def waiting_content_wrong_type(message: Message) -> None:
    await message.answer(
        "Надішли текст, одне фото або одне фото з текстом. Бот не вередує, але інші формати він поки не жує.",
        reply_markup=cancel_keyboard(),
    )

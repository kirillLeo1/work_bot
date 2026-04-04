from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.config import Settings
from bot.constants import MAIN_SECTIONS
from bot.keyboards.common import cancel_keyboard, section_categories_keyboard
from bot.services.repository import create_submission, get_submission, get_user_by_telegram_id
from bot.states import SubmissionState
from bot.utils.formatters import submission_text

router = Router()


@router.message(F.text.in_(list(MAIN_SECTIONS.keys())))
async def section_selected(message: Message, state: FSMContext) -> None:
    user = await get_user_by_telegram_id(message.from_user.id)
    if not user or user.is_admin:
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
    await state.set_state(SubmissionState.waiting_for_text)
    await message.answer(
        f"Обрано: <b>{section}</b>\nНапиши текст повідомлення.",
        reply_markup=cancel_keyboard(),
    )


@router.callback_query(F.data.startswith("category:"))
async def category_selected(callback: CallbackQuery, state: FSMContext) -> None:
    user = await get_user_by_telegram_id(callback.from_user.id)
    if not user or user.is_admin:
        await callback.answer()
        return

    _, section, category = callback.data.split(":", 2)
    await state.update_data(section=section, category=category)
    await state.set_state(SubmissionState.waiting_for_text)
    await callback.message.answer(
        f"Розділ: <b>{section}</b>\nПідрозділ: <b>{category}</b>\nНапиши текст звіту або повідомлення.",
        reply_markup=cancel_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "cancel_action")
async def cancel_action(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.answer("Дію скасовано.")
    await callback.answer()


@router.message(SubmissionState.waiting_for_text)
async def save_submission(message: Message, state: FSMContext, settings: Settings) -> None:
    user = await get_user_by_telegram_id(message.from_user.id)
    if not user or user.is_admin:
        return

    data = await state.get_data()
    submission = await create_submission(
        user_id=user.id,
        section=data["section"],
        category=data.get("category"),
        text=message.text.strip(),
    )
    submission = await get_submission(submission.id)
    await state.clear()

    await message.answer("Готово. Повідомлення збережено і відправлено керівникам.")

    for admin_id in settings.admin_ids:
        try:
            await message.bot.send_message(
                admin_id,
                submission_text(submission),
                reply_markup=__import__("bot.keyboards.common", fromlist=["admin_submission_actions"]).admin_submission_actions(submission.id),
            )
        except Exception:
            continue

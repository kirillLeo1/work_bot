from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.config import Settings
from bot.constants import ADMIN_SWITCH_TO_PANEL, ADMIN_SWITCH_TO_REPORTS
from bot.keyboards.common import admin_main_menu, admin_reports_menu, worker_main_menu
from bot.services.repository import get_user_by_telegram_id
from bot.states import RegistrationState

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext, settings: Settings) -> None:
    telegram_id = message.from_user.id
    user = await get_user_by_telegram_id(telegram_id)
    if user:
        if user.is_admin:
            await message.answer("Ти вже в системі як керівник.", reply_markup=admin_main_menu())
        else:
            await message.answer("Ти вже в системі. Обирай розділ.", reply_markup=worker_main_menu())
        return

    is_admin = telegram_id in settings.admin_ids
    await state.update_data(is_admin=is_admin)
    await state.set_state(RegistrationState.first_name)
    role_text = "керівника" if is_admin else "працівника"
    await message.answer(f"Привіт. Реєструємо акаунт {role_text}.\nВведи ім’я.")


@router.message(RegistrationState.first_name)
async def reg_first_name(message: Message, state: FSMContext) -> None:
    await state.update_data(first_name=message.text.strip())
    await state.set_state(RegistrationState.last_name)
    await message.answer("Тепер введи прізвище.")


@router.message(RegistrationState.last_name)
async def reg_last_name(message: Message, state: FSMContext) -> None:
    await state.update_data(last_name=message.text.strip())
    await state.set_state(RegistrationState.employee_number)
    await message.answer("Тепер введи номер працівника.")


@router.message(RegistrationState.employee_number)
async def reg_employee_number(message: Message, state: FSMContext) -> None:
    from bot.services.repository import create_or_update_user

    data = await state.get_data()
    user = await create_or_update_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=data["first_name"],
        last_name=data["last_name"],
        employee_number=message.text.strip(),
        is_admin=bool(data.get("is_admin", False)),
    )
    await state.clear()

    if user.is_admin:
        await message.answer("Готово. Ти зареєстрований як керівник.", reply_markup=admin_main_menu())
    else:
        await message.answer("Готово. Ти зареєстрований як працівник.", reply_markup=worker_main_menu())


@router.message(F.text == "/menu")
async def menu_handler(message: Message) -> None:
    user = await get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("Спочатку натисни /start")
        return
    if user.is_admin:
        await message.answer("Меню керівника:", reply_markup=admin_main_menu())
    else:
        await message.answer("Меню працівника:", reply_markup=worker_main_menu())


@router.message(F.text == ADMIN_SWITCH_TO_REPORTS)
async def switch_admin_to_reports(message: Message) -> None:
    user = await get_user_by_telegram_id(message.from_user.id)
    if not user or not user.is_admin:
        return
    await message.answer("Режим звітів увімкнено. Обирай розділ.", reply_markup=admin_reports_menu())


@router.message(F.text == ADMIN_SWITCH_TO_PANEL)
async def switch_admin_to_panel(message: Message) -> None:
    user = await get_user_by_telegram_id(message.from_user.id)
    if not user or not user.is_admin:
        return
    await message.answer("Повернув у адмін-панель.", reply_markup=admin_main_menu())

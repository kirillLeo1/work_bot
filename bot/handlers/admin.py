from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.common import admin_submission_actions, workers_list_keyboard
from bot.services.repository import (
    add_reply,
    close_submission,
    get_submission,
    get_user_by_telegram_id,
    get_worker_submissions,
    list_recent_submissions,
    list_workers,
)
from bot.states import AdminReplyState
from bot.utils.formatters import submission_text, worker_label

router = Router()


async def ensure_admin(telegram_id: int):
    user = await get_user_by_telegram_id(telegram_id)
    return user if user and user.is_admin else None


@router.message(F.text == "📥 Нові звернення")
async def new_submissions(message: Message) -> None:
    admin = await ensure_admin(message.from_user.id)
    if not admin:
        return
    submissions = await list_recent_submissions(limit=20, only_new=True)
    if not submissions:
        await message.answer("Нових звернень зараз немає.")
        return
    for item in submissions:
        await message.answer(submission_text(item), reply_markup=admin_submission_actions(item.id))


@router.message(F.text == "📊 Всі звернення")
async def all_submissions(message: Message) -> None:
    admin = await ensure_admin(message.from_user.id)
    if not admin:
        return
    submissions = await list_recent_submissions(limit=20, only_new=False)
    if not submissions:
        await message.answer("Поки звернень немає.")
        return
    for item in submissions:
        await message.answer(submission_text(item), reply_markup=admin_submission_actions(item.id))


@router.message(F.text == "👷 Працівники")
async def workers_view(message: Message) -> None:
    admin = await ensure_admin(message.from_user.id)
    if not admin:
        return
    workers = await list_workers()
    if not workers:
        await message.answer("Поки немає зареєстрованих працівників.")
        return
    payload = [(worker.id, worker_label(worker)) for worker in workers]
    await message.answer("Оберіть працівника:", reply_markup=workers_list_keyboard(payload))


@router.callback_query(F.data.startswith("worker:"))
async def worker_history(callback: CallbackQuery) -> None:
    admin = await ensure_admin(callback.from_user.id)
    if not admin:
        await callback.answer()
        return
    user_id = int(callback.data.split(":", 1)[1])
    submissions = await get_worker_submissions(user_id)
    if not submissions:
        await callback.message.answer("У цього працівника ще немає звернень.")
    else:
        for item in submissions:
            item = await get_submission(item.id)
            await callback.message.answer(submission_text(item), reply_markup=admin_submission_actions(item.id))
    await callback.answer()


@router.callback_query(F.data.startswith("reply:"))
async def reply_start(callback: CallbackQuery, state: FSMContext) -> None:
    admin = await ensure_admin(callback.from_user.id)
    if not admin:
        await callback.answer()
        return
    submission_id = int(callback.data.split(":", 1)[1])
    await state.set_state(AdminReplyState.waiting_for_reply)
    await state.update_data(submission_id=submission_id)
    await callback.message.answer(f"Напиши відповідь для звернення ID {submission_id}.")
    await callback.answer()


@router.message(AdminReplyState.waiting_for_reply)
async def send_reply(message: Message, state: FSMContext) -> None:
    admin = await ensure_admin(message.from_user.id)
    if not admin:
        return
    data = await state.get_data()
    submission_id = int(data["submission_id"])
    await add_reply(submission_id=submission_id, admin_telegram_id=message.from_user.id, text=message.text.strip())
    submission = await get_submission(submission_id)
    await state.clear()

    await message.answer("Відповідь збережено і відправлено працівнику.")
    await message.bot.send_message(
        submission.user.telegram_id,
        (
            f"<b>Відповідь керівника</b>\n"
            f"На звернення ID: <code>{submission.id}</code>\n"
            f"Розділ: <b>{submission.section}</b>\n"
            f"Підрозділ: <b>{submission.category or '—'}</b>\n\n"
            f"{message.text.strip()}"
        ),
    )


@router.callback_query(F.data.startswith("close:"))
async def close_item(callback: CallbackQuery) -> None:
    admin = await ensure_admin(callback.from_user.id)
    if not admin:
        await callback.answer()
        return
    submission_id = int(callback.data.split(":", 1)[1])
    await close_submission(submission_id)
    submission = await get_submission(submission_id)
    await callback.message.answer(f"Звернення ID {submission_id} закрито.")
    try:
        await callback.bot.send_message(
            submission.user.telegram_id,
            f"Твоє звернення ID <code>{submission_id}</code> закрито керівником.",
        )
    except Exception:
        pass
    await callback.answer("Закрито")

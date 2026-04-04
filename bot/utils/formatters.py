from __future__ import annotations

from bot.db import Submission, User


def worker_label(user: User) -> str:
    return f"{user.first_name} {user.last_name} #{user.employee_number}"


def submission_text(submission: Submission) -> str:
    user = submission.user
    category_line = submission.category if submission.category else "—"
    username_line = f"@{user.username}" if user and user.username else "немає"
    return (
        f"<b>Нове звернення</b>\n"
        f"ID: <code>{submission.id}</code>\n"
        f"Працівник: <b>{user.first_name} {user.last_name}</b>\n"
        f"Номер: <b>{user.employee_number}</b>\n"
        f"Telegram: {username_line}\n"
        f"Розділ: <b>{submission.section}</b>\n"
        f"Підрозділ: <b>{category_line}</b>\n"
        f"Статус: <b>{submission.status}</b>\n\n"
        f"<b>Текст:</b>\n{submission.text}"
    )

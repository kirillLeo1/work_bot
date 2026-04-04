from __future__ import annotations

from sqlalchemy import Select, desc, select, update
from sqlalchemy.orm import selectinload

from bot.db import Reply, Submission, User, get_session


async def get_user_by_telegram_id(telegram_id: int) -> User | None:
    async with get_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalar_one_or_none()


async def create_or_update_user(
    telegram_id: int,
    username: str | None,
    first_name: str,
    last_name: str,
    employee_number: str,
    is_admin: bool,
) -> User:
    async with get_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        if user is None:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                employee_number=employee_number,
                is_admin=is_admin,
            )
            session.add(user)
        else:
            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            user.employee_number = employee_number
            user.is_admin = is_admin
        await session.commit()
        await session.refresh(user)
        return user


async def create_submission(user_id: int, section: str, category: str | None, text: str) -> Submission:
    async with get_session() as session:
        submission = Submission(user_id=user_id, section=section, category=category, text=text)
        session.add(submission)
        await session.commit()
        await session.refresh(submission)
        return submission


async def get_submission(submission_id: int) -> Submission | None:
    async with get_session() as session:
        stmt: Select[tuple[Submission]] = (
            select(Submission)
            .where(Submission.id == submission_id)
            .options(selectinload(Submission.user), selectinload(Submission.replies))
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


async def add_reply(submission_id: int, admin_telegram_id: int, text: str) -> Reply:
    async with get_session() as session:
        reply = Reply(submission_id=submission_id, admin_telegram_id=admin_telegram_id, text=text)
        session.add(reply)
        await session.execute(
            update(Submission).where(Submission.id == submission_id).values(status="answered")
        )
        await session.commit()
        await session.refresh(reply)
        return reply


async def close_submission(submission_id: int) -> None:
    async with get_session() as session:
        await session.execute(
            update(Submission).where(Submission.id == submission_id).values(status="closed")
        )
        await session.commit()


async def list_recent_submissions(limit: int = 20, only_new: bool = False) -> list[Submission]:
    async with get_session() as session:
        stmt = select(Submission).options(selectinload(Submission.user)).order_by(desc(Submission.created_at)).limit(limit)
        if only_new:
            stmt = stmt.where(Submission.status == "new")
        result = await session.execute(stmt)
        return list(result.scalars().all())


async def list_workers() -> list[User]:
    async with get_session() as session:
        result = await session.execute(
            select(User).where(User.is_admin.is_(False)).order_by(User.last_name, User.first_name)
        )
        return list(result.scalars().all())


async def get_worker_submissions(user_id: int, limit: int = 20) -> list[Submission]:
    async with get_session() as session:
        result = await session.execute(
            select(Submission)
            .where(Submission.user_id == user_id)
            .options(selectinload(Submission.user))
            .order_by(desc(Submission.created_at))
            .limit(limit)
        )
        return list(result.scalars().all())

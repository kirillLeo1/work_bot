from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, Text, func, inspect, text
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str] = mapped_column(String(255))
    last_name: Mapped[str] = mapped_column(String(255))
    employee_number: Mapped[str] = mapped_column(String(100), index=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    submissions: Mapped[list["Submission"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    section: Mapped[str] = mapped_column(String(255), index=True)
    category: Mapped[str | None] = mapped_column(String(255), nullable=True)
    text: Mapped[str] = mapped_column(Text)
    photo_file_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    photo_unique_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="new", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)

    user: Mapped[User] = relationship(back_populates="submissions")
    replies: Mapped[list["Reply"]] = relationship(back_populates="submission", cascade="all, delete-orphan")


class Reply(Base):
    __tablename__ = "replies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey("submissions.id"), index=True)
    admin_telegram_id: Mapped[int] = mapped_column(BigInteger, index=True)
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    submission: Mapped[Submission] = relationship(back_populates="replies")


engine = None
session_factory: async_sessionmaker[AsyncSession] | None = None


def setup_database(database_url: str) -> None:
    global engine, session_factory
    engine = create_async_engine(database_url, pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def _ensure_submission_columns() -> None:
    if engine is None:
        raise RuntimeError("Database is not initialized")

    async with engine.begin() as conn:
        def _has_column(sync_conn, table_name: str, column_name: str) -> bool:
            inspector = inspect(sync_conn)
            columns = {column["name"] for column in inspector.get_columns(table_name)}
            return column_name in columns

        has_photo_file_id = await conn.run_sync(_has_column, "submissions", "photo_file_id")
        if not has_photo_file_id:
            await conn.execute(text("ALTER TABLE submissions ADD COLUMN photo_file_id VARCHAR(255) NULL"))

        has_photo_unique_id = await conn.run_sync(_has_column, "submissions", "photo_unique_id")
        if not has_photo_unique_id:
            await conn.execute(text("ALTER TABLE submissions ADD COLUMN photo_unique_id VARCHAR(255) NULL"))


async def create_tables() -> None:
    if engine is None:
        raise RuntimeError("Database is not initialized")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await _ensure_submission_columns()


@asynccontextmanager
async def get_session() -> AsyncSession:
    if session_factory is None:
        raise RuntimeError("Database is not initialized")
    async with session_factory() as session:
        yield session

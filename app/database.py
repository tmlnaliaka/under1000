from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from app.config import settings


class Base(DeclarativeBase):
    pass


_engine: Optional[AsyncSession] = None
_session_maker: Optional[async_sessionmaker] = None


def get_engine():
    global _engine
    if _engine is None:
        connect_args = {"check_same_thread": False} if "sqlite" in settings.database_url else {}
        kwargs = {"connect_args": connect_args}
        if "sqlite" not in settings.database_url:
            kwargs.update({"pool_pre_ping": True, "pool_size": 5, "max_overflow": 10})
        _engine = create_async_engine(settings.database_url, echo=settings.env == "development", **kwargs)
    return _engine


def get_session_maker():
    global _session_maker
    if _session_maker is None:
        _session_maker = async_sessionmaker(get_engine(), expire_on_commit=False, class_=AsyncSession)
    return _session_maker


def configure_db(url: str):
    global _engine, _session_maker
    connect_args = {"check_same_thread": False} if "sqlite" in url else {}
    kwargs = {"connect_args": connect_args}
    if "sqlite" not in url:
        kwargs.update({"pool_pre_ping": True, "pool_size": 5, "max_overflow": 10})
    _engine = create_async_engine(url, echo=False, **kwargs)
    _session_maker = async_sessionmaker(_engine, expire_on_commit=False, class_=AsyncSession)
    return _engine, _session_maker


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with get_session_maker()() as session:
        yield session


async def init_db() -> None:
    async with get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

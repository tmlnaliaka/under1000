import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import tempfile
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.main import create_app
from app.database import Base

_engine = None
_Session = None
_tmp_name = None


def _get_or_create_db():
    global _engine, _Session, _tmp_name
    if _engine is None:
        tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        _tmp_name = tmp.name
        tmp.close()
        url = f"sqlite+aiosqlite:///{_tmp_name}"
        _engine = create_async_engine(url, connect_args={"check_same_thread": False})
        async def init():
            async with _engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            return _engine
        import asyncio
        asyncio.get_event_loop().run_until_complete(init())
        _Session = async_sessionmaker(_engine, expire_on_commit=False, class_=AsyncSession)
    return _engine, _Session


@pytest_asyncio.fixture(scope="session")
async def _db_setup():
    global _engine, _Session, _tmp_name
    _get_or_create_db()
    yield
    if _engine:
        await _engine.dispose()
    try:
        os.remove(_tmp_name)
    except OSError:
        pass


@pytest_asyncio.fixture
async def db(_db_setup):
    async with _Session() as session:
        yield session


@pytest_asyncio.fixture
async def client(db):
    app = create_app()

    async def _get_db_override():
        yield db

    from app.database import get_db as app_get_db
    app.dependency_overrides[app_get_db] = _get_db_override
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", follow_redirects=False) as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def user_token(client):
    await client.post("/api/auth/register", json={
        "username": "authtest",
        "email": "authtest@example.com",
        "password": "testpass123",
    })
    resp = await client.post("/api/auth/login", data={"username": "authtest", "password": "testpass123"})
    return resp.json()["access_token"]


@pytest_asyncio.fixture
async def auth_client(client, user_token):
    client.headers["Authorization"] = f"Bearer {user_token}"
    return client

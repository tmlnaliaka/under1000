import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import tempfile
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.main import create_app
from app.database import Base


@pytest_asyncio.fixture
async def db():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp_name = tmp.name
    tmp.close()
    url = f"sqlite+aiosqlite:///{tmp_name}"
    engine = create_async_engine(url, connect_args={"check_same_thread": False})
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    Session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    session = Session()
    yield session
    await session.close()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
    try:
        os.remove(tmp_name)
    except OSError:
        pass


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

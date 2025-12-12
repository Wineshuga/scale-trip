import os
import sys
import pytest
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from httpx import ASGITransport, AsyncClient

# --- Fix import path ---
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

# Ensure tests use the TEST database and tell the app we're testing
from app.config import TEST_DATABASE_URL
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["TESTING"] = "1"

# import app after setting env vars so app.database uses TEST_DATABASE_URL
from app.main import app
import app.database as database
from app.database import get_session

# Create a dedicated async engine for tests and a session factory
engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, future=True
)

# Make sure app.database uses the test engine/session factory too
# so all parts of the app that import database will share the same engine
database.engine = engine
database.async_session = AsyncSessionLocal

# Dependency override to force handlers to use the test session
async def override_get_session():
    async with AsyncSessionLocal() as session:
        yield session

# Create/drop tables around each test to ensure isolation
@pytest.fixture(scope="function", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    try:
        yield
    finally:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
        # Dispose connections to ensure a clean slate between tests
        await engine.dispose()

# Async HTTP client fixture that runs the ASGI app directly
@pytest.fixture()
async def client():
    app.dependency_overrides[get_session] = override_get_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

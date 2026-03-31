import pytest
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport
from motor.motor_asyncio import AsyncIOMotorClient

from main import app
from app.db.connection import get_db
from app.config import settings


@pytest.fixture
def mock_db_connected():
    """Mock Motor database that responds to ping successfully."""
    db = MagicMock()
    db.command = AsyncMock(return_value={"ok": 1})
    return db


@pytest.fixture
def mock_db_disconnected():
    """Mock Motor database that raises an exception on ping."""
    db = MagicMock()
    db.command = AsyncMock(side_effect=Exception("Connection refused"))
    return db


@pytest.fixture
async def client_connected(mock_db_connected):
    """Async test client with a connected mock DB."""
    async def override_get_db():
        yield mock_db_connected

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def client_disconnected(mock_db_disconnected):
    """Async test client with a disconnected mock DB."""
    async def override_get_db():
        yield mock_db_disconnected

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Real test-database fixtures (Phase 4)
# ---------------------------------------------------------------------------

TEST_DB_NAME = "smart_personal_cfo_test"


@pytest.fixture
async def test_db():
    """Yield a real Motor database handle pointing at the test DB."""
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[TEST_DB_NAME]
    yield db
    # Clean up all documents inserted during the test
    await db["transactions"].delete_many({})
    client.close()


@pytest.fixture
async def real_client(test_db):
    """Async test client wired to the real test MongoDB database."""
    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

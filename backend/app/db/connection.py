from typing import AsyncGenerator

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import settings

_client: AsyncIOMotorClient | None = None


async def connect_db() -> None:
    """Create the Motor client on application startup."""
    global _client
    _client = AsyncIOMotorClient(settings.MONGODB_URI)


async def close_db() -> None:
    """Close the Motor client on application shutdown."""
    global _client
    if _client is not None:
        _client.close()
        _client = None


async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """Async generator that yields the Motor database handle.

    Usable as a FastAPI dependency via Depends(get_db).
    """
    yield _client[settings.DATABASE_NAME]

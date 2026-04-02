from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.connection import get_db

router = APIRouter()


@router.get("/", status_code=200)
async def health_check(db: AsyncIOMotorDatabase = Depends(get_db)):
    try:
        await db.command("ping")
        return {
            "status": "ok",
            "database": "connected",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception:
        raise HTTPException(
            status_code=503,
            detail={"status": "degraded", "database": "disconnected"},
        )

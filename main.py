from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.connection import connect_db, close_db
from app.routers.health import router as health_router
from app.routers.transactions import router as transactions_router
from app.routers.analytics import router as analytics_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()


app = FastAPI(title="Smart Personal CFO", lifespan=lifespan)
app.include_router(health_router, prefix="/health", tags=["Health"])
app.include_router(transactions_router)
app.include_router(analytics_router)

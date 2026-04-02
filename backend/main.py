from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # <--- Added this

from app.db.connection import connect_db, close_db
from app.routers.health import router as health_router
from app.routers.transactions import router as transactions_router
from app.routers.analytics import router as analytics_router
from app.routers.auth import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()

app = FastAPI(title="Smart Personal CFO", lifespan=lifespan)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

app.include_router(health_router, prefix="/health", tags=["Health"])
app.include_router(transactions_router)
app.include_router(analytics_router)
app.include_router(auth_router)
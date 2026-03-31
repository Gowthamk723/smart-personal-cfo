from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.connection import get_db
from app.schemas.transaction import TransactionCreate, TransactionRead, UploadResponse
from app.services.ocr import extract_text
from app.services.parser import parse_receipt

router = APIRouter(prefix="/transactions", tags=["Transactions"])

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png"}
UPLOADS_DIR = Path("uploads")


@router.post("/", response_model=TransactionRead, status_code=201)
async def save_transaction(
    payload: TransactionCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> TransactionRead:
    doc = payload.model_dump()
    doc["created_at"] = datetime.now(timezone.utc)
    try:
        result = await db["transactions"].insert_one(doc)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Database insertion failed: {exc}") from exc
    doc["_id"] = result.inserted_id
    return TransactionRead.model_validate(doc)


@router.get("/", response_model=list[TransactionRead])
async def list_transactions(
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> list[TransactionRead]:
    cursor = db["transactions"].find()
    docs = await cursor.to_list(length=None)
    return [TransactionRead.model_validate(doc) for doc in docs]


@router.post("/upload/", response_model=UploadResponse)
async def upload_transaction_image(file: UploadFile = File(...)) -> UploadResponse:
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(400, detail=f"Unsupported file type: {file.content_type}")

    UPLOADS_DIR.mkdir(exist_ok=True)
    extension = Path(file.filename).suffix  # .jpg or .png
    unique_name = f"{uuid4()}{extension}"
    file_path = UPLOADS_DIR / unique_name

    contents = await file.read()
    file_path.write_bytes(contents)

    raw_text = extract_text(str(file_path))
    parsed = parse_receipt(raw_text)
    return UploadResponse(
        file_path=str(file_path),
        raw_text=raw_text,
        merchant=parsed.merchant_name,
        date=parsed.date,
        amount=parsed.amount,
        category=parsed.category,
    )

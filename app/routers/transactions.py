from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.transaction import UploadResponse
from app.services.ocr import extract_text
from app.services.parser import parse_receipt

router = APIRouter(prefix="/transactions", tags=["Transactions"])

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png"}
UPLOADS_DIR = Path("uploads")


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

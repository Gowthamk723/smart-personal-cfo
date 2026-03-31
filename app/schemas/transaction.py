from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from app.schemas import FinancialType


class TransactionCreate(BaseModel):
    amount: Decimal = Field(..., decimal_places=2)
    type: FinancialType
    category_id: str = Field(..., min_length=1)
    date: datetime
    description: str | None = Field(default=None, max_length=500)

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("amount must be greater than 0")
        return v


class TransactionRead(TransactionCreate):
    id: str
    user_id: str
    created_at: datetime


class UploadResponse(BaseModel):
    file_path: str
    raw_text: str
    merchant: str | None = None
    date: str | None = None
    amount: str | None = None
    category: str | None = None

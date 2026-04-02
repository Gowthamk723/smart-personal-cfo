from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator, field_serializer, model_validator
from pydantic.config import ConfigDict

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

    @field_serializer("amount")
    def serialise_amount(self, v: Decimal) -> float:
        return float(v)


class TransactionRead(TransactionCreate):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(validation_alias="_id")
    created_at: datetime

    @model_validator(mode="before")
    @classmethod
    def coerce_id(cls, data: dict) -> dict:
        if "_id" in data and not isinstance(data["_id"], str):
            data["_id"] = str(data["_id"])
        return data


class UploadResponse(BaseModel):
    file_path: str
    raw_text: str
    merchant: str | None = None
    date: str | None = None
    amount: str | None = None
    category: str | None = None

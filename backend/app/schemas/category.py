from pydantic import BaseModel, Field, field_validator

from app.schemas import FinancialType


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: FinancialType

    @field_validator("name")
    @classmethod
    def strip_name_whitespace(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("name must not be empty or whitespace only")
        return stripped


class CategoryRead(CategoryCreate):
    id: str
    user_id: str

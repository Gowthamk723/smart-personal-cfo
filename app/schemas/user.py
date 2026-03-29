from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr, field_validator


class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("password must be at least 8 characters")
        return v


class UserRead(BaseModel):
    id: str
    email: EmailStr
    created_at: datetime
    is_active: bool = True

    model_config = {"populate_by_name": True}

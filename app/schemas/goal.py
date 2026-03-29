from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class GoalCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    target_amount: Decimal = Field(..., decimal_places=2)
    deadline: datetime | None = None

    @field_validator("target_amount")
    @classmethod
    def target_amount_must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("target_amount must be greater than 0")
        return v


class GoalRead(GoalCreate):
    id: str
    user_id: str
    current_amount: Decimal = Decimal("0.00")
    created_at: datetime

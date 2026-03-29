from datetime import datetime, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.transaction import TransactionCreate
from app.schemas import FinancialType


def _base_data(**kwargs):
    data = {
        "amount": Decimal("10.00"),
        "type": FinancialType.income,
        "category_id": "cat123",
        "date": datetime.now(timezone.utc),
    }
    data.update(kwargs)
    return data


def test_valid_income_transaction():
    t = TransactionCreate(**_base_data(type=FinancialType.income))
    assert t.type == FinancialType.income
    assert t.amount == Decimal("10.00")


def test_valid_expense_transaction():
    t = TransactionCreate(**_base_data(type=FinancialType.expense))
    assert t.type == FinancialType.expense


def test_amount_zero_raises():
    with pytest.raises(ValidationError) as exc_info:
        TransactionCreate(**_base_data(amount=Decimal("0")))
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("amount",) for e in errors)


def test_amount_negative_raises():
    with pytest.raises(ValidationError) as exc_info:
        TransactionCreate(**_base_data(amount=Decimal("-1")))
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("amount",) for e in errors)


def test_invalid_type_raises():
    with pytest.raises(ValidationError) as exc_info:
        TransactionCreate(**_base_data(type="transfer"))
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("type",) for e in errors)


def test_optional_description_accepted():
    t = TransactionCreate(**_base_data(description="A" * 500))
    assert len(t.description) == 500


def test_description_too_long_raises():
    with pytest.raises(ValidationError):
        TransactionCreate(**_base_data(description="A" * 501))


def test_no_description_is_valid():
    t = TransactionCreate(**_base_data())
    assert t.description is None

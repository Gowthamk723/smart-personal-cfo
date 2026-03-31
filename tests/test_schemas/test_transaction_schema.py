"""Tests for TransactionRead _id mapping and Decimal serialisation."""
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from bson import ObjectId
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from app.schemas import FinancialType
from app.schemas.transaction import TransactionCreate, TransactionRead


# ── helpers ──────────────────────────────────────────────────────────────────

def _read_data(**kwargs):
    data = {
        "_id": ObjectId(),
        "amount": Decimal("10.00"),
        "type": FinancialType.income,
        "category_id": "cat123",
        "date": datetime.now(timezone.utc),
        "created_at": datetime.now(timezone.utc),
    }
    data.update(kwargs)
    return data


# ── 1.1 Unit tests for TransactionRead _id mapping ───────────────────────────

def test_objectid_coerced_to_nonempty_string():
    t = TransactionRead.model_validate(_read_data())
    assert isinstance(t.id, str)
    assert len(t.id) > 0


def test_string_id_preserved():
    t = TransactionRead.model_validate(_read_data(_id="abc123"))
    assert t.id == "abc123"


def test_model_dump_json_has_no_underscore_id_key():
    t = TransactionRead.model_validate(_read_data())
    dumped = t.model_dump(mode="json")
    assert "_id" not in dumped


# ── 1.2 Property 4: Decimal serialises as a JSON number ──────────────────────
# Feature: smart-personal-cfo, Property 4: Decimal serialises as a JSON number

@given(
    amount=st.decimals(
        min_value="0.01",
        max_value="1000000",
        allow_nan=False,
        allow_infinity=False,
        places=2,
    )
)
@settings(max_examples=100)
def test_decimal_serialises_as_json_number(amount):
    """Validates: Requirements 4.5"""
    data = _read_data(amount=amount)
    t = TransactionRead.model_validate(data)
    dumped = t.model_dump(mode="json")
    assert isinstance(dumped["amount"], (float, int)), (
        f"Expected float/int, got {type(dumped['amount'])}: {dumped['amount']!r}"
    )


# ── 1.3 Property 3: TransactionCreate validation rejects invalid amounts ──────
# Feature: smart-personal-cfo, Property 3: TransactionCreate validation rejects invalid amounts

@given(
    amount=st.decimals(
        max_value="0",
        allow_nan=False,
        allow_infinity=False,
    )
)
@settings(max_examples=100)
def test_invalid_amount_raises_validation_error(amount):
    """Validates: Requirements 4.1"""
    with pytest.raises(ValidationError):
        TransactionCreate(
            amount=amount,
            type=FinancialType.income,
            category_id="cat1",
            date=datetime.now(timezone.utc),
        )


@given(
    amount=st.decimals(
        min_value="0.01",
        max_value="1000000",
        allow_nan=False,
        allow_infinity=False,
        places=2,
    )
)
@settings(max_examples=100)
def test_positive_amount_succeeds(amount):
    """Validates: Requirements 4.1"""
    t = TransactionCreate(
        amount=amount,
        type=FinancialType.income,
        category_id="cat1",
        date=datetime.now(timezone.utc),
    )
    assert t.amount == amount

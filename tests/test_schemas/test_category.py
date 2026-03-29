import pytest
from pydantic import ValidationError

from app.schemas.category import CategoryCreate
from app.schemas import FinancialType


def test_valid_category():
    cat = CategoryCreate(name="Food", type=FinancialType.expense)
    assert cat.name == "Food"
    assert cat.type == FinancialType.expense


def test_name_whitespace_stripped():
    cat = CategoryCreate(name="  Salary  ", type=FinancialType.income)
    assert cat.name == "Salary"


def test_empty_name_raises():
    with pytest.raises(ValidationError) as exc_info:
        CategoryCreate(name="", type=FinancialType.expense)
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("name",) for e in errors)


def test_whitespace_only_name_raises():
    with pytest.raises(ValidationError) as exc_info:
        CategoryCreate(name="   ", type=FinancialType.expense)
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("name",) for e in errors)


def test_name_over_100_chars_raises():
    with pytest.raises(ValidationError) as exc_info:
        CategoryCreate(name="A" * 101, type=FinancialType.expense)
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("name",) for e in errors)


def test_name_exactly_100_chars_valid():
    cat = CategoryCreate(name="A" * 100, type=FinancialType.income)
    assert len(cat.name) == 100

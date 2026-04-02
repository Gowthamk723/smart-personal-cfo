from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.schemas.user import UserCreate, UserRead


def test_valid_user_create():
    user = UserCreate(email="test@example.com", password="securepass")
    assert user.email == "test@example.com"
    assert user.password == "securepass"


def test_invalid_email_raises():
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(email="not-an-email", password="securepass")
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("email",) for e in errors)


def test_short_password_raises():
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(email="test@example.com", password="short")
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("password",) for e in errors)


def test_password_exactly_8_chars_valid():
    user = UserCreate(email="test@example.com", password="exactly8")
    assert user.password == "exactly8"


def test_user_read_no_password_field():
    user = UserRead(
        id="abc123",
        email="test@example.com",
        created_at=datetime.now(timezone.utc),
        is_active=True,
    )
    dumped = user.model_dump()
    assert "password" not in dumped

from datetime import datetime, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.goal import GoalCreate


def test_valid_goal_without_deadline():
    goal = GoalCreate(name="Emergency Fund", target_amount=Decimal("1000.00"))
    assert goal.name == "Emergency Fund"
    assert goal.target_amount == Decimal("1000.00")
    assert goal.deadline is None


def test_valid_goal_with_deadline():
    deadline = datetime(2025, 12, 31, tzinfo=timezone.utc)
    goal = GoalCreate(name="Vacation", target_amount=Decimal("500.00"), deadline=deadline)
    assert goal.deadline == deadline


def test_target_amount_zero_raises():
    with pytest.raises(ValidationError) as exc_info:
        GoalCreate(name="Test", target_amount=Decimal("0"))
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("target_amount",) for e in errors)


def test_target_amount_negative_raises():
    with pytest.raises(ValidationError) as exc_info:
        GoalCreate(name="Test", target_amount=Decimal("-50.00"))
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("target_amount",) for e in errors)


def test_name_over_200_chars_raises():
    with pytest.raises(ValidationError) as exc_info:
        GoalCreate(name="A" * 201, target_amount=Decimal("100.00"))
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("name",) for e in errors)


def test_name_exactly_200_chars_valid():
    goal = GoalCreate(name="A" * 200, target_amount=Decimal("100.00"))
    assert len(goal.name) == 200

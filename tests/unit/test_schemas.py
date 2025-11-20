import pytest
from pydantic import ValidationError
from app.schemas import UserCreate

def test_usercreate_valid():
    user = UserCreate(
        username="anvith",
        email="test@example.com",
        password="password123"
    )
    assert user.username == "anvith"

def test_usercreate_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(
            username="anvith",
            email="not-an-email",
            password="password123"
        )

def test_usercreate_short_password():
    with pytest.raises(ValidationError):
        UserCreate(
            username="anvith",
            email="test@example.com",
            password="123"
        )

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import Optional

from app.models import CalcType

class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=128)

class UserRead(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class CalculationCreate(BaseModel):
    a: float
    b: float
    type: CalcType
    user_id: Optional[int] = None

    @model_validator(mode="after")
    def check_division_by_zero(self):
        # for Divide operations, b must not be zero
        if self.type == CalcType.Divide and self.b == 0:
            raise ValueError("Division by zero is not allowed")
        return self


class CalculationRead(BaseModel):
    id: int
    a: float
    b: float
    type: CalcType
    result: Optional[float]
    user_id: Optional[int]

    class Config:
        from_attributes = True

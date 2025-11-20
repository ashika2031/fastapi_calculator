from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

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

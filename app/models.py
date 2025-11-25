from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from .database import Base
from sqlalchemy import Float, ForeignKey
from sqlalchemy.orm import relationship
from enum import Enum


class CalcType(str, Enum):
    Add = "Add"
    Sub = "Sub"
    Multiply = "Multiply"
    Divide = "Divide"

class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("username", name="uq_users_username"),
        UniqueConstraint("email", name="uq_users_email"),
    )

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )


class Calculation(Base):
    __tablename__ = "calculations"

    id = Column(Integer, primary_key=True, index=True)
    a = Column(Float, nullable=False)
    b = Column(Float, nullable=False)
    type = Column(String(20), nullable=False)
    # store result to make queries and tests deterministic
    result = Column(Float, nullable=True)
    # optional reference to a user who requested the calculation
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    user = relationship("User", backref="calculations")

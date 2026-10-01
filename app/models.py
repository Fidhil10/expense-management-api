"""SQLAlchemy ORM models for User, Expense, and Salary.

Defines the database schemas and relationships for users, expense entries,
and salary records.
"""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


def utc_now() -> datetime:
    """Return timezone-naive or aware UTC datetime for SQLite compatibility."""
    return datetime.now(timezone.utc)


class User(Base):
    """User account model for authentication and data ownership."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, nullable=False
    )

    # Relationships
    expenses: Mapped[List["Expense"]] = relationship(
        "Expense", back_populates="user", cascade="all, delete-orphan"
    )
    salaries: Mapped[List["Salary"]] = relationship(
        "Salary", back_populates="user", cascade="all, delete-orphan"
    )


class Expense(Base):
    """Expense data model tracking financial expenditures.

    Attributes:
        id: Primary key identifier.
        name: Name or description of the expense.
        amount: Monetary amount spent.
        category: Expenditure category (e.g. Food, Transport, Utilities).
        created_at: Timestamp when expense was recorded or occurred.
        user_id: Foreign key to owning user account.
    """

    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, index=True, nullable=False
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship(
        "User", back_populates="expenses"
    )


class Salary(Base):
    """Salary or income data model for tracking earnings.

    Attributes:
        id: Primary key identifier.
        amount: Monetary income amount.
        created_at: Timestamp when income was recorded.
        user_id: Foreign key to owning user account.
    """

    __tablename__ = "salaries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, index=True, nullable=False
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship(
        "User", back_populates="salaries"
    )
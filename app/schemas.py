"""Pydantic schemas for request validation and response serialization.

Follows Pydantic v2 best practices with strict typing, field constraints,
and documentation examples.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------
# User & Authentication Schemas
# ---------------------------------------------------------

class UserBase(BaseModel):
    """Base schema for user fields."""
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique username for the account",
        examples=["john_doe"],
    )
    email: str = Field(
        ...,
        min_length=5,
        max_length=100,
        description="Unique email address",
        examples=["john@example.com"],
    )


class UserCreate(UserBase):
    """Payload for registering a new user."""
    password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        description="Plain text password (minimum 6 characters)",
        examples=["SecurePass123!"],
    )


class UserLogin(BaseModel):
    """Payload for JSON-based user login."""
    username: str = Field(..., examples=["john_doe"])
    password: str = Field(..., examples=["SecurePass123!"])


class UserOut(UserBase):
    """Public representation of user details."""
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """OAuth2 Bearer token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Decoded token payload."""
    username: Optional[str] = None


# ---------------------------------------------------------
# Expense Schemas
# ---------------------------------------------------------

class ExpenseCreate(BaseModel):
    """Payload for creating a new expense."""
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Name or title of the expense",
        examples=["Grocery Shopping"],
    )
    amount: float = Field(
        ...,
        gt=0,
        description="Positive numerical amount spent",
        examples=[120.50],
    )
    category: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Category classification for the expense",
        examples=["Food"],
    )
    created_at: Optional[datetime] = Field(
        default=None,
        description="Optional timestamp. Defaults to current UTC datetime if omitted.",
        examples=["2026-10-01T12:00:00"],
    )


class ExpenseUpdate(BaseModel):
    """Payload for modifying an existing expense."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    amount: Optional[float] = Field(default=None, gt=0)
    category: Optional[str] = Field(default=None, min_length=1, max_length=50)
    created_at: Optional[datetime] = None


class ExpenseOut(BaseModel):
    """Expense response representation conforming to requirement specifications."""
    expense_id: int = Field(description="Unique identifier for the expense")
    name: str
    amount: float
    category: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------
# Salary & Totals Schemas
# ---------------------------------------------------------

class SalaryCreate(BaseModel):
    """Payload for adding a salary or income entry."""
    amount: float = Field(
        ...,
        gt=0,
        description="Positive monetary salary/income amount",
        examples=[5000.0],
    )
    created_at: Optional[datetime] = Field(
        default=None,
        description="Optional timestamp for the salary entry",
        examples=["2026-10-01T00:00:00"],
    )


class SalaryOut(BaseModel):
    """Representation of a salary record."""
    salary_id: int
    amount: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Totals(BaseModel):
    """Overall financial metrics summarizing expenses, salary, and savings."""
    total_expense: float = Field(
        description="Sum total of all recorded expenses",
        examples=[1250.75],
    )
    total_salary: float = Field(
        description="Sum total of all recorded salary/income entries",
        examples=[5000.0],
    )
    remaining_amount: float = Field(
        description="Remaining balance (total_salary - total_expense)",
        examples=[3749.25],
    )


class MonthlyTotals(Totals):
    """Financial metrics scoped to a specific year and month."""
    year: int = Field(examples=[2026])
    month: int = Field(examples=[10])

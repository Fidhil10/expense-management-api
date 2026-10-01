"""Financial totals and salary management endpoints.

Calculates aggregated metrics (total expenses, total salary, remaining amount)
and manages income records.
"""

import calendar
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.deps import get_current_user
from app.models import Expense, Salary, User
from app.schemas import MonthlyTotals, SalaryCreate, SalaryOut, Totals

router = APIRouter(tags=["Financial Totals & Salary"])


@router.post(
    "/salary/",
    response_model=SalaryOut,
    status_code=status.HTTP_201_CREATED,
    summary="Add salary/income entry",
    description="Record an income or salary entry to compute remaining balance.",
)
async def add_salary(
    data: SalaryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SalaryOut:
    """Record a new salary or income entry."""
    salary_data = data.model_dump()
    if salary_data.get("created_at") is None:
        salary_data["created_at"] = datetime.now(timezone.utc)

    salary = Salary(
        amount=salary_data["amount"],
        created_at=salary_data["created_at"],
        user_id=current_user.id if current_user else None,
    )
    db.add(salary)
    await db.commit()
    await db.refresh(salary)

    return SalaryOut(
        salary_id=salary.id,
        amount=salary.amount,
        created_at=salary.created_at,
    )


@router.get(
    "/salary/",
    response_model=List[SalaryOut],
    summary="List all salary/income entries",
    description="Retrieve all recorded salary entries for the authenticated user.",
)
async def list_salaries(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[SalaryOut]:
    """Retrieve all salary entries for the user."""
    query = select(Salary)
    if current_user:
        query = query.where(Salary.user_id == current_user.id)

    query = query.order_by(Salary.created_at.desc())
    rows = await db.scalars(query)
    return [
        SalaryOut(salary_id=s.id, amount=s.amount, created_at=s.created_at)
        for s in rows
    ]


@router.get(
    "/totals/",
    response_model=Totals,
    summary="Get total expenses, total salary, and remaining amount",
    description=(
        "Compute cumulative financial totals: total expenses, total salary, "
        "and net remaining balance."
    ),
)
async def get_totals(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Totals:
    """Calculate cumulative expense, salary, and remaining financial balance."""
    expense_query = select(func.coalesce(func.sum(Expense.amount), 0.0))
    salary_query = select(func.coalesce(func.sum(Salary.amount), 0.0))

    if current_user:
        expense_query = expense_query.where(Expense.user_id == current_user.id)
        salary_query = salary_query.where(Salary.user_id == current_user.id)

    total_expense = float(await db.scalar(expense_query) or 0.0)
    total_salary = float(await db.scalar(salary_query) or 0.0)
    remaining_amount = round(total_salary - total_expense, 2)

    return Totals(
        total_expense=round(total_expense, 2),
        total_salary=round(total_salary, 2),
        remaining_amount=remaining_amount,
    )


@router.get(
    "/totals/month/{year}/{month}/",
    response_model=MonthlyTotals,
    summary="Get monthly totals and remaining amount",
    description="Compute monthly total expenses, salary, and remaining amount for a specific month.",
)
async def get_monthly_totals(
    year: int,
    month: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MonthlyTotals:
    """Calculate monthly financial totals for a specified year and month."""
    if month < 1 or month > 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Month must be between 1 and 12.",
        )
    if year < 1900 or year > 2100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Year must be between 1900 and 2100.",
        )

    _, last_day = calendar.monthrange(year, month)
    start_dt = datetime(year, month, 1, 0, 0, 0)
    end_dt = datetime(year, month, last_day, 23, 59, 59, 999999)

    expense_query = select(func.coalesce(func.sum(Expense.amount), 0.0)).where(
        Expense.created_at >= start_dt,
        Expense.created_at <= end_dt,
    )
    salary_query = select(func.coalesce(func.sum(Salary.amount), 0.0)).where(
        Salary.created_at >= start_dt,
        Salary.created_at <= end_dt,
    )

    if current_user:
        expense_query = expense_query.where(Expense.user_id == current_user.id)
        salary_query = salary_query.where(Salary.user_id == current_user.id)

    total_expense = float(await db.scalar(expense_query) or 0.0)
    total_salary = float(await db.scalar(salary_query) or 0.0)
    remaining_amount = round(total_salary - total_expense, 2)

    return MonthlyTotals(
        year=year,
        month=month,
        total_expense=round(total_expense, 2),
        total_salary=round(total_salary, 2),
        remaining_amount=remaining_amount,
    )
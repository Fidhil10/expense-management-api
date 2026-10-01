"""Expense endpoints for creating, retrieving, updating, and filtering expenses.

Provides full REST operations and robust filtering by month, week, day,
and category, with user-level data isolation and authentication.
"""

import calendar
from datetime import date, datetime, time, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.deps import get_current_user
from app.models import Expense, User
from app.schemas import ExpenseCreate, ExpenseOut, ExpenseUpdate

router = APIRouter(prefix="/expenses", tags=["Expenses"])


def to_out(e: Expense) -> ExpenseOut:
    """Map ORM Expense entity to the required ExpenseOut schema format."""
    return ExpenseOut(
        expense_id=e.id,
        name=e.name,
        amount=e.amount,
        category=e.category,
        created_at=e.created_at,
    )


@router.post(
    "/",
    response_model=ExpenseOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new expense",
    description="Record a new expense item with name, amount, category, and optional custom date.",
)
async def create_expense(
    data: ExpenseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ExpenseOut:
    """Create a new expense associated with the authenticated user."""
    expense_data = data.model_dump()
    if expense_data.get("created_at") is None:
        expense_data["created_at"] = datetime.now(timezone.utc)

    expense = Expense(
        name=expense_data["name"],
        amount=expense_data["amount"],
        category=expense_data["category"],
        created_at=expense_data["created_at"],
        user_id=current_user.id if current_user else None,
    )
    db.add(expense)
    await db.commit()
    await db.refresh(expense)
    return to_out(expense)


@router.get(
    "/",
    response_model=List[ExpenseOut],
    summary="Retrieve all expenses with optional filters",
    description=(
        "Retrieve expenses belonging to the authenticated user. "
        "Supports query filters by category, year, month, week, day, and pagination."
    ),
)
async def list_expenses(
    category: Optional[str] = Query(None, description="Filter by category"),
    year: Optional[int] = Query(None, ge=1900, le=2100, description="Filter by year"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Filter by month (1-12)"),
    week: Optional[int] = Query(None, ge=1, le=53, description="Filter by ISO week number (1-53)"),
    day: Optional[int] = Query(None, ge=1, le=31, description="Filter by day of month (1-31)"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(100, ge=1, le=1000, description="Pagination limit"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[ExpenseOut]:
    """Retrieve expenses with flexible query parameters."""
    query = select(Expense)
    if current_user:
        query = query.where(Expense.user_id == current_user.id)

    if category:
        query = query.where(func.lower(Expense.category) == category.strip().lower())

    # Date range filters based on provided parameters
    if year and month and day:
        try:
            target_date = date(year, month, day)
            start_dt = datetime.combine(target_date, time.min)
            end_dt = datetime.combine(target_date, time.max)
            query = query.where(Expense.created_at >= start_dt, Expense.created_at <= end_dt)
        except ValueError as err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid date: {err}",
            )
    elif year and month:
        try:
            _, last_day = calendar.monthrange(year, month)
            start_dt = datetime(year, month, 1, 0, 0, 0)
            end_dt = datetime(year, month, last_day, 23, 59, 59, 999999)
            query = query.where(Expense.created_at >= start_dt, Expense.created_at <= end_dt)
        except ValueError as err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid month or year: {err}",
            )
    elif year and week:
        try:
            start_dt = datetime.combine(date.fromisocalendar(year, week, 1), time.min)
            end_dt = datetime.combine(date.fromisocalendar(year, week, 7), time.max)
            query = query.where(Expense.created_at >= start_dt, Expense.created_at <= end_dt)
        except ValueError as err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid ISO week or year: {err}",
            )
    elif year:
        start_dt = datetime(year, 1, 1, 0, 0, 0)
        end_dt = datetime(year, 12, 31, 23, 59, 59, 999999)
        query = query.where(Expense.created_at >= start_dt, Expense.created_at <= end_dt)

    query = query.order_by(Expense.created_at.desc(), Expense.id.desc()).offset(skip).limit(limit)
    rows = await db.scalars(query)
    return [to_out(e) for e in rows]


@router.get(
    "/month/{year}/{month}/",
    response_model=List[ExpenseOut],
    summary="Filter expenses by month",
    description="Retrieve all expenses for a specific year and month.",
)
async def expenses_by_month(
    year: int,
    month: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[ExpenseOut]:
    """Retrieve expenses for a specific month and year."""
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

    query = select(Expense).where(
        Expense.created_at >= start_dt,
        Expense.created_at <= end_dt,
    )
    if current_user:
        query = query.where(Expense.user_id == current_user.id)

    query = query.order_by(Expense.created_at.desc())
    rows = await db.scalars(query)
    return [to_out(e) for e in rows]


@router.get(
    "/week/{year}/{week}/",
    response_model=List[ExpenseOut],
    summary="Filter expenses by ISO week",
    description="Retrieve all expenses for a specific year and ISO week number (1-53).",
)
async def expenses_by_week(
    year: int,
    week: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[ExpenseOut]:
    """Retrieve expenses for a specific ISO calendar week."""
    if week < 1 or week > 53:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Week must be between 1 and 53.",
        )
    try:
        start_dt = datetime.combine(date.fromisocalendar(year, week, 1), time.min)
        end_dt = datetime.combine(date.fromisocalendar(year, week, 7), time.max)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid ISO week calculation: {err}",
        )

    query = select(Expense).where(
        Expense.created_at >= start_dt,
        Expense.created_at <= end_dt,
    )
    if current_user:
        query = query.where(Expense.user_id == current_user.id)

    query = query.order_by(Expense.created_at.desc())
    rows = await db.scalars(query)
    return [to_out(e) for e in rows]


@router.get(
    "/day/{year}/{month}/{day}/",
    response_model=List[ExpenseOut],
    summary="Filter expenses by day",
    description="Retrieve all expenses for a specific date (year, month, day).",
)
async def expenses_by_day(
    year: int,
    month: int,
    day: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[ExpenseOut]:
    """Retrieve expenses for a specific calendar day."""
    try:
        target_date = date(year, month, day)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid date: {err}",
        )

    start_dt = datetime.combine(target_date, time.min)
    end_dt = datetime.combine(target_date, time.max)

    query = select(Expense).where(
        Expense.created_at >= start_dt,
        Expense.created_at <= end_dt,
    )
    if current_user:
        query = query.where(Expense.user_id == current_user.id)

    query = query.order_by(Expense.created_at.desc())
    rows = await db.scalars(query)
    return [to_out(e) for e in rows]


@router.get(
    "/category/{category}/",
    response_model=List[ExpenseOut],
    summary="Filter expenses by category",
    description="Retrieve all expenses matching a specific category (case-insensitive).",
)
async def expenses_by_category(
    category: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[ExpenseOut]:
    """Retrieve expenses matching a specified category name."""
    query = select(Expense).where(
        func.lower(Expense.category) == category.strip().lower()
    )
    if current_user:
        query = query.where(Expense.user_id == current_user.id)

    query = query.order_by(Expense.created_at.desc())
    rows = await db.scalars(query)
    return [to_out(e) for e in rows]


@router.get(
    "/{expense_id}",
    response_model=ExpenseOut,
    summary="Get single expense by ID",
    description="Retrieve detailed information for a single expense entry.",
)
async def get_expense(
    expense_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ExpenseOut:
    """Retrieve an expense by ID ensuring user ownership."""
    query = select(Expense).where(Expense.id == expense_id)
    if current_user:
        query = query.where(Expense.user_id == current_user.id)

    expense = await db.scalar(query)
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found",
        )
    return to_out(expense)


@router.put(
    "/{expense_id}",
    response_model=ExpenseOut,
    summary="Update an existing expense",
    description="Modify the name, amount, category, or date of an existing expense.",
)
async def update_expense(
    expense_id: int,
    data: ExpenseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ExpenseOut:
    """Update fields of an existing expense."""
    query = select(Expense).where(Expense.id == expense_id)
    if current_user:
        query = query.where(Expense.user_id == current_user.id)

    expense = await db.scalar(query)
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found",
        )

    update_dict = data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(expense, field, value)

    await db.commit()
    await db.refresh(expense)
    return to_out(expense)


@router.delete(
    "/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an expense",
    description="Remove an expense entry from the database.",
)
async def delete_expense(
    expense_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete an expense belonging to the current user."""
    query = select(Expense).where(Expense.id == expense_id)
    if current_user:
        query = query.where(Expense.user_id == current_user.id)

    expense = await db.scalar(query)
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found",
        )

    await db.delete(expense)
    await db.commit()
# Expense Management API

A production-grade, asynchronous RESTful API built with **FastAPI**, **SQLAlchemy 2.0 (async)**, and **SQLite (aiosqlite)** for tracking expenses, managing salary income, computing financial analytics (totals and remaining balance), and performing multi-dimensional filtering (by month, week, day, and category).

Includes complete **OAuth2 password flow authentication** with signed **JWT bearer tokens** and automatic interactive API documentation via **Swagger UI** and **ReDoc**.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Architecture](#project-architecture)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Configuration](#environment-configuration)
  - [Database Initialization & Running Server](#database-initialization--running-server)
- [Interactive API Documentation](#interactive-api-documentation)
- [Authentication Workflow](#authentication-workflow)
- [API Reference & Examples](#api-reference--examples)
  - [Authentication Endpoints](#authentication-endpoints)
  - [Expense Management Endpoints](#expense-management-endpoints)
  - [Date & Category Filter Endpoints](#date--category-filter-endpoints)
  - [Salary & Financial Totals Endpoints](#salary--financial-totals-endpoints)
- [Automated Testing](#automated-testing)
- [Submission & Git Instructions](#submission--git-instructions)

---

## Features

### 1. Functional Requirements
- **Expense Model**: Modeled with `name` (string), `amount` (float, > 0), `category` (string), `created_at` (timestamp), and primary key `expense_id` / `id`.
- **Create Expense API (`POST /expenses/`)**: Validates input and persists expense, returning full details including auto-generated `expense_id`.
- **Get Expenses API (`GET /expenses/`)**: Retrieves all expenses scoped to the user, with pagination (`skip`, `limit`) and flexible query filters.
- **Multi-Dimensional Date & Category Filtering**:
  - Filter by specific month: `GET /expenses/month/{year}/{month}/`
  - Filter by ISO week: `GET /expenses/week/{year}/{week}/`
  - Filter by calendar day: `GET /expenses/day/{year}/{month}/{day}/`
  - Filter by category: `GET /expenses/category/{category}/` (case-insensitive)
  - Universal query parameter filtering on root: `GET /expenses/?category=...&year=...&month=...`
- **Financial Analytics & Totals (`GET /totals/`)**:
  - Aggregates `total_expense`, `total_salary`, and `remaining_amount` (`total_salary - total_expense`).
  - Supports adding income via `POST /salary/` and viewing income history with `GET /salary/`.
  - Supports monthly totals breakdown: `GET /totals/month/{year}/{month}/`.

### 2. Non-Functional & Security Requirements
- **Asynchronous Architecture**: Fully async database interactions utilizing `SQLAlchemy 2.0` and `aiosqlite`.
- **OAuth2 + JWT Authentication**: Secure user registration, password hashing via `bcrypt`, and JWT token verification.
- **Data Scoping & Isolation**: Users can only create, view, update, and aggregate their own financial records.
- **Comprehensive Test Suite**: 28 automated unit and integration tests using `pytest` and `httpx.AsyncClient` with 100% pass rate.
- **PEP 8 Compliance**: Fully typed, formatted, and documented according to standard Python guidelines.

---

## Tech Stack

| Component | Technology |
|---|---|
| Framework | **FastAPI 0.136+** |
| ASGI Server | **Uvicorn** |
| ORM | **SQLAlchemy 2.0 (Async)** |
| Database | **SQLite** via **aiosqlite** (pluggable for PostgreSQL) |
| Data Validation | **Pydantic v2** & **pydantic-settings** |
| Authentication | **OAuth2 Password Flow** with **python-jose (JWT)** & **bcrypt** |
| Test Suite | **Pytest** & **pytest-asyncio** with **httpx** |

---

## Project Architecture

```text
.
├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py          # App settings & environment configurations
│   │   └── security.py        # Bcrypt password hashing & JWT encoding/decoding
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py            # Authentication endpoints (register, token, login, me)
│   │   ├── expenses.py        # CRUD & date/category filter endpoints for expenses
│   │   └── totals.py          # Salary management & financial metrics endpoints
│   ├── database.py            # Async engine, SessionLocal, and DB dependencies
│   ├── deps.py                # Security dependencies (get_current_user, OAuth2)
│   ├── main.py                # FastAPI app instance, lifespan, CORS, and routing
│   ├── models.py              # SQLAlchemy ORM models (User, Expense, Salary)
│   └── schemas.py             # Pydantic v2 schemas for request & response models
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # In-memory async SQLite engine & test client fixtures
│   ├── test_auth.py           # Unit tests for authentication
│   ├── test_expenses.py       # Unit tests for expense creation, retrieval, and CRUD
│   ├── test_filters.py        # Unit tests for month, week, day, and category filters
│   └── test_totals.py         # Unit tests for salary and financial total calculations
├── .env.example               # Example environment variable file
├── .gitignore                 # Git ignore rules for Python, SQLite, and IDEs
├── requirements.txt           # Python package dependencies
└── README.md                  # Complete project documentation
```

---

## Getting Started

### Prerequisites
- Python 3.10+ (tested and verified on Python 3.13)
- `pip` package manager

### Installation

1. Clone or navigate to the project directory:
   ```bash
   cd e:/PROJECT/ff
   ```

2. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Environment Configuration

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Default configuration values:
- `DATABASE_URL`: `sqlite+aiosqlite:///./expenses.db`
- `SECRET_KEY`: Secure random key for JWT signing
- `ALGORITHM`: `HS256`
- `ACCESS_TOKEN_EXPIRE_MINUTES`: `1440` (24 hours)
- `REQUIRE_AUTH`: `true`

### Database Initialization & Running Server

Launch the development server with live reload:
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Database tables (`users`, `expenses`, `salaries`) are automatically created during startup by the application lifespan handler.

---

## Interactive API Documentation

FastAPI provides interactive OpenAPI documentation out-of-the-box:

- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **OpenAPI JSON**: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

---

## Authentication Workflow

Endpoints are protected by OAuth2 Bearer Authentication. Follow these simple steps:

1. **Register**: Send a `POST` request to `/auth/register` with `username`, `email`, and `password`.
2. **Obtain Token**: Send a `POST` request to `/auth/token` (or `/auth/login`) to receive a JWT `access_token`.
3. **Authorize**:
   - In **Swagger UI**: Click the **Authorize 🔓** button at the top right, enter your credentials, and click **Authorize**.
   - In **cURL / HTTP Client**: Include the header `Authorization: Bearer <your_access_token>`.

---

## API Reference & Examples

### Authentication Endpoints

#### 1. Register User
```bash
curl -X POST "http://127.0.0.1:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alex",
    "email": "alex@example.com",
    "password": "Password123!"
  }'
```
**Response (201 Created):**
```json
{
  "username": "alex",
  "email": "alex@example.com",
  "id": 1,
  "created_at": "2026-10-01T14:00:00Z"
}
```

#### 2. Obtain Token (OAuth2 Form Login)
```bash
curl -X POST "http://127.0.0.1:8000/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alex&password=Password123!"
```
**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer"
}
```

---

### Expense Management Endpoints

#### 3. Create Expense (`POST /expenses/`)
```bash
curl -X POST "http://127.0.0.1:8000/expenses/" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Groceries",
    "amount": 120.50,
    "category": "Food"
  }'
```
**Response (201 Created):**
```json
{
  "expense_id": 1,
  "name": "Groceries",
  "amount": 120.5,
  "category": "Food",
  "created_at": "2026-10-01T14:15:00Z"
}
```

#### 4. List Expenses (`GET /expenses/`)
```bash
curl -X GET "http://127.0.0.1:8000/expenses/" \
  -H "Authorization: Bearer <TOKEN>"
```
**Response (200 OK):**
```json
[
  {
    "expense_id": 1,
    "name": "Groceries",
    "amount": 120.5,
    "category": "Food",
    "created_at": "2026-10-01T14:15:00Z"
  }
]
```

---

### Date & Category Filter Endpoints

#### 5. Filter Expenses by Month (`GET /expenses/month/{year}/{month}/`)
```bash
curl -X GET "http://127.0.0.1:8000/expenses/month/2026/10/" \
  -H "Authorization: Bearer <TOKEN>"
```

#### 6. Filter Expenses by Week (`GET /expenses/week/{year}/{week}/`)
```bash
curl -X GET "http://127.0.0.1:8000/expenses/week/2026/40/" \
  -H "Authorization: Bearer <TOKEN>"
```

#### 7. Filter Expenses by Day (`GET /expenses/day/{year}/{month}/{day}/`)
```bash
curl -X GET "http://127.0.0.1:8000/expenses/day/2026/10/1/" \
  -H "Authorization: Bearer <TOKEN>"
```

#### 8. Filter Expenses by Category (`GET /expenses/category/{category}/`)
```bash
curl -X GET "http://127.0.0.1:8000/expenses/category/food/" \
  -H "Authorization: Bearer <TOKEN>"
```

---

### Salary & Financial Totals Endpoints

#### 9. Add Salary (`POST /salary/`)
```bash
curl -X POST "http://127.0.0.1:8000/salary/" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 5000.00
  }'
```
**Response (201 Created):**
```json
{
  "salary_id": 1,
  "amount": 5000.0,
  "created_at": "2026-10-01T14:20:00Z"
}
```

#### 10. Get Totals (`GET /totals/`)
```bash
curl -X GET "http://127.0.0.1:8000/totals/" \
  -H "Authorization: Bearer <TOKEN>"
```
**Response (200 OK):**
```json
{
  "total_expense": 120.5,
  "total_salary": 5000.0,
  "remaining_amount": 4879.5
}
```

#### 11. Get Monthly Totals (`GET /totals/month/{year}/{month}/`)
```bash
curl -X GET "http://127.0.0.1:8000/totals/month/2026/10/" \
  -H "Authorization: Bearer <TOKEN>"
```
**Response (200 OK):**
```json
{
  "year": 2026,
  "month": 10,
  "total_expense": 120.5,
  "total_salary": 5000.0,
  "remaining_amount": 4879.5
}
```

---

## Automated Testing

The project includes 28 asynchronous tests covering all evaluation criteria and edge cases.

To execute tests:
```bash
pytest -v
```

Output:
```text
tests/test_auth.py::test_register_user_success PASSED                    [  3%]
tests/test_auth.py::test_register_duplicate_username PASSED              [  7%]
tests/test_auth.py::test_register_duplicate_email PASSED                 [ 10%]
tests/test_auth.py::test_oauth2_token_login_success PASSED               [ 14%]
tests/test_auth.py::test_json_login_success PASSED                       [ 17%]
tests/test_auth.py::test_login_invalid_password PASSED                   [ 21%]
tests/test_auth.py::test_get_current_user_profile PASSED                 [ 25%]
tests/test_auth.py::test_get_current_user_unauthorized PASSED            [ 28%]
tests/test_expenses.py::test_create_expense_unauthenticated PASSED       [ 32%]
tests/test_expenses.py::test_list_expenses_unauthenticated PASSED        [ 35%]
tests/test_expenses.py::test_create_expense_success PASSED               [ 39%]
tests/test_expenses.py::test_create_expense_validation_error PASSED      [ 42%]
tests/test_expenses.py::test_list_expenses_success PASSED                [ 46%]
tests/test_expenses.py::test_get_single_expense PASSED                   [ 50%]
tests/test_expenses.py::test_update_expense PASSED                       [ 53%]
tests/test_expenses.py::test_delete_expense PASSED                       [ 57%]
tests/test_expenses.py::test_expense_user_isolation PASSED               [ 60%]
tests/test_filters.py::test_filter_by_month_endpoint PASSED              [ 64%]
tests/test_filters.py::test_filter_by_month_validation PASSED            [ 67%]
tests/test_filters.py::test_filter_by_week PASSED                        [ 71%]
tests/test_filters.py::test_filter_by_day PASSED                         [ 75%]
tests/test_filters.py::test_filter_by_category PASSED                    [ 78%]
tests/test_filters.py::test_query_parameters_filter PASSED               [ 82%]
tests/test_totals.py::test_totals_empty PASSED                           [ 85%]
tests/test_totals.py::test_add_salary_and_calculate_totals PASSED        [ 89%]
tests/test_totals.py::test_list_salaries PASSED                          [ 92%]
tests/test_totals.py::test_monthly_totals PASSED                         [ 96%]
tests/test_totals.py::test_totals_user_isolation PASSED                  [100%]

============================= 28 passed in 39.24s =============================
```

---

## Submission & Git Instructions

To publish this project to GitHub as requested in the submission instructions:

1. **Initialize and stage changes**:
   ```bash
   git add .
   git commit -m "feat: complete FastAPI expense management application with auth, filters, and totals"
   ```

2. **Create a new repository on GitHub** (e.g. named `fastapi-expense-management`).

3. **Link remote and push**:
   ```bash
   git remote add origin https://github.com/<your-username>/fastapi-expense-management.git
   git branch -M main
   git push -u origin main
   ```

4. **Provide your repository URL** for evaluation.
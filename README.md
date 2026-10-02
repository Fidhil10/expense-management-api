# Expense Management API

## Setup

```bash
pip install -r requirements.txt
```

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Swagger docs: http://127.0.0.1:8000/docs

---

## Quick Start Examples

---

### 1. Register a User

1. Expand **POST `/auth/register`** and click **Try it out**
2. Enter the request body:
```json
{
  "username": "fidhil",
  "email": "fidhil@example.com",
  "password": "secret123"
}
```
3. Click **Execute** — returns the created user details

---

### 2. Login and Get Token

1. Expand **POST `/auth/token`** and click **Try it out**
2. Enter `username` and `password` in the form fields
3. Click **Execute** — copy the `access_token` from the response
4. Click **Authorize** (top right in Swagger) and paste the token to access protected endpoints

---

### 3. Add an Expense

1. Expand **POST `/expenses/`** and click **Try it out**
2. Enter the request body:
```json
{
  "name": "Lunch",
  "amount": 250,
  "category": "Food"
}
```
3. Click **Execute** — response shows the saved expense with its ID

---

### 4. View All Expenses

1. Expand **GET `/expenses/`** and click **Try it out**
2. Click **Execute** — returns the list of all saved expenses

---

### 5. Filter Expenses by Month

1. Expand **GET `/expenses/month/{year}/{month}/`** and click **Try it out**
2. Enter values, for example:
   - `year`: `2026`
   - `month`: `10`
3. Click **Execute** — returns all expenses for October 2026

---

### 6. Filter Expenses by Week

1. Expand **GET `/expenses/week/{year}/{week}/`** and click **Try it out**
2. Enter values, for example:
   - `year`: `2026`
   - `week`: `40`
3. Click **Execute** — returns all expenses in that ISO week

---

### 7. Filter Expenses by Day

1. Expand **GET `/expenses/day/{year}/{month}/{day}/`** and click **Try it out**
2. Enter values, for example:
   - `year`: `2026`
   - `month`: `10`
   - `day`: `2`
3. Click **Execute** — returns all expenses for that specific day

---

### 8. Filter Expenses by Category

1. Expand **GET `/expenses/category/{category}/`** and click **Try it out**
2. Enter value, for example:
   - `category`: `Food`
3. Click **Execute** — returns all expenses under that category

---

### 9. Add Salary

1. Expand **POST `/salary/`** and click **Try it out**
2. Enter the request body:
```json
{
  "amount": 50000,
  "description": "Monthly salary"
}
```
3. Click **Execute**

---

### 10. View Salary History

1. Expand **GET `/salary/`** and click **Try it out**
2. Click **Execute** — returns all salary/income entries

---

### 11. View Totals

1. Expand **GET `/totals/`** and click **Try it out**
2. Click **Execute** — returns `total_expense`, `total_salary`, and `remaining_amount`

---

### 12. View Monthly Totals

1. Expand **GET `/totals/month/{year}/{month}/`** and click **Try it out**
2. Enter values, for example:
   - `year`: `2026`
   - `month`: `10`
3. Click **Execute** — returns totals breakdown for that month

---

## Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/token` | Login and get JWT token |

### Expenses
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/expenses/` | Create an expense |
| GET | `/expenses/` | Get all expenses |
| GET | `/expenses/month/{year}/{month}/` | Filter by month |
| GET | `/expenses/week/{year}/{week}/` | Filter by week |
| GET | `/expenses/day/{year}/{month}/{day}/` | Filter by day |
| GET | `/expenses/category/{category}/` | Filter by category |

### Salary & Totals
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/salary/` | Add salary/income |
| GET | `/salary/` | Get salary history |
| GET | `/totals/` | Get total expense, income & balance |
| GET | `/totals/month/{year}/{month}/` | Monthly totals |
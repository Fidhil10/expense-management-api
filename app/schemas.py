from datetime import datetime
from typing import Optional

from pydantic import BaseModel,ConfigDict,Field


class UserBase(BaseModel):
    username:str=Field(...,min_length=3,max_length=50)
    email:str=Field(...,min_length=5,max_length=100)


class UserCreate(UserBase):
    password:str=Field(...,min_length=6,max_length=128)


class UserLogin(BaseModel):
    username:str
    password:str


class UserOut(UserBase):
    id:int
    created_at:datetime

    model_config=ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token:str
    token_type:str="bearer"


class TokenData(BaseModel):
    username:Optional[str]=None


class ExpenseCreate(BaseModel):
    name:str=Field(...,min_length=1,max_length=100)
    amount:float=Field(...,gt=0)
    category:str=Field(...,min_length=1,max_length=50)
    created_at:Optional[datetime]=None


class ExpenseUpdate(BaseModel):
    name:Optional[str]=Field(default=None,min_length=1,max_length=100)
    amount:Optional[float]=Field(default=None,gt=0)
    category:Optional[str]=Field(default=None,min_length=1,max_length=50)
    created_at:Optional[datetime]=None


class ExpenseOut(BaseModel):
    expense_id:int
    name:str
    amount:float
    category:str
    created_at:datetime

    model_config=ConfigDict(from_attributes=True)


class SalaryCreate(BaseModel):
    amount:float=Field(...,gt=0)
    created_at:Optional[datetime]=None


class SalaryOut(BaseModel):
    salary_id:int
    amount:float
    created_at:datetime

    model_config=ConfigDict(from_attributes=True)


class Totals(BaseModel):
    total_expense:float
    total_salary:float
    remaining_amount:float


class MonthlyTotals(Totals):
    year:int
    month:int
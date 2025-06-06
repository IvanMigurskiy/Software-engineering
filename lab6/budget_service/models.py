from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date
from enum import Enum


class Periodicity(str, Enum):
    ONCE = "once" 
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class Income(BaseModel):
    income_id: str
    title: str
    value: int
    due_date: Optional[date] = None
    periodicity: Periodicity = Periodicity.ONCE
    periodicity_value: Optional[int]
    username: str

class IncomeCreate(BaseModel):
    title: str
    value: int
    due_date: Optional[date] = None
    periodicity: Periodicity = Periodicity.ONCE
    periodicity_value: Optional[int]

class Cost(BaseModel):
    cost_id: str
    title: str
    value: int
    due_date: Optional[date] = None
    periodicity: Periodicity = Periodicity.ONCE
    periodicity_value: Optional[int]
    username: str

class CostCreate(BaseModel):
    title: str
    value: int
    due_date: Optional[date] = None
    periodicity: Periodicity = Periodicity.ONCE
    periodicity_value: Optional[int]

class Budget(BaseModel):
    value:  int
    due_date: date

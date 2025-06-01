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
    income_id: int
    title: str
    value: int
    due_date: Optional[date] = None
    periodicity: Periodicity = Periodicity.ONCE
    periodicity_value: Optional[int]
    username: str

class Cost(BaseModel):
    cost_id: int
    title: str
    value: int
    due_date: Optional[date] = None
    periodicity: Periodicity = Periodicity.ONCE
    periodicity_value: Optional[int]
    username: str

class Budget(BaseModel):
    value:  int
    due_date: date

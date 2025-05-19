from fastapi import FastAPI, HTTPException, Depends, status, Request
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime, date
import logging
import os
from typing import List, Optional
import httpx
import psycopg2
from psycopg2.extras import RealDictCursor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8000")
DB_CONFIG = {
    "dbname": "budget_tracker",
    "user": "postgres",
    "password": "postgres",
    "host": "postgres",
    "port": "5432"
}

class Role(str, Enum):
    CLIENT = "client"
    ADMIN = "admin"

class Periodicity(str, Enum):
    ONCE = "once" 
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class UserPublic(BaseModel):
    user_id: int
    username: str
    full_name: Optional[str]
    role: Role

class Income(BaseModel):
    income_id: int
    title: str
    description: str
    value:  Optional[int] = None
    due_date: Optional[date] = None
    periodicity: Periodicity = Periodicity.ONCE
    periodicity_value: Optional[int]
    created_at: datetime
    updated_at: datetime
    assignee_id: Optional[int] = None

class IncomeCreate(BaseModel):
    title: str = Field(..., max_length=100)
    description: str
    value:  Optional[int] = None
    due_date: Optional[date] = None
    periodicity: Periodicity = Periodicity.ONCE
    periodicity_value: Optional[int]
    assignee_id: Optional[int] = None

class Cost(BaseModel):
    cost_id: int
    title: str
    description: str
    value:  Optional[int] = None
    due_date: Optional[date] = None
    periodicity: Periodicity = Periodicity.ONCE
    periodicity_value: Optional[int]
    created_at: datetime
    updated_at: datetime
    assignee_id: Optional[int] = None

class CostCreate(BaseModel):
    title: str = Field(..., max_length=100)
    description: str
    value:  Optional[int] = None
    due_date: Optional[date] = None
    periodicity: Periodicity = Periodicity.ONCE
    periodicity_value: Optional[int]
    assignee_id: Optional[int] = None

class Budget(BaseModel):
    value:  Optional[int] = None
    created_at: datetime
    due_date: Optional[date] = None

class BudgetCreate(BaseModel):
    due_date: Optional[date] = None
    value:  Optional[int] = None

app = FastAPI()

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

async def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    token = auth_header.split(" ")[1] if " " in auth_header else auth_header
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{AUTH_SERVICE_URL}/auth/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Could not validate credentials")
        return UserPublic(**response.json())

@app.post("/incomes/", status_code=status.HTTP_201_CREATED, response_model=Income)
async def create_income(income: IncomeCreate, current_user: UserPublic = Depends(get_current_user)):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO incomes (title, description, value, due_date, periodicity, periodicity_value, assignee_id, creator_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING *
                """,
                (income.title, income.description, income.value, income.due_date, income.periodicity.value,
                 income.periodicity_value, income.assignee_id, current_user.user_id)
            )
            new_income = cur.fetchone()
            conn.commit()
    return Income(**new_income)

@app.get("/incomes/", response_model=List[Income])
async def read_incomes(current_user: UserPublic = Depends(get_current_user)):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM incomes WHERE assignee_id = %s",
                        (current_user.user_id))
            incomes = cur.fetchall()
    return [Income(**income) for income in incomes]

@app.get("/incomes/{income_id}", response_model=Income)
async def read_income(income_id: int, current_user: UserPublic = Depends(get_current_user)):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM incomes WHERE income_id = %s AND assignee_id = %s",
                        (income_id, current_user.user_id))
            income = cur.fetchone()
    if not income:
        raise HTTPException(status_code=404, detail="Income not found")
    return Income(**income)

@app.post("/costs/", status_code=status.HTTP_201_CREATED, response_model=Cost)
async def create_cost(cost: CostCreate, current_user: UserPublic = Depends(get_current_user)):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO costs (title, description, value, due_date, periodicity, periodicity_value, assignee_id, creator_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING *
                """,
                (cost.title, cost.description, cost.value, cost.due_date, cost.periodicity.value,
                  cost.periodicity_value, cost.assignee_id, current_user.user_id)
            )
            new_cost = cur.fetchone()
            conn.commit()
    return Cost(**new_cost)

@app.get("/costs/", response_model=List[Cost])
async def read_costs(current_user: UserPublic = Depends(get_current_user)):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM costs WHERE assignee_id = %s",
                        (current_user.user_id))
            costs = cur.fetchall()
    return [Cost(**cost) for cost in costs]

@app.get("/costs/{cost_id}", response_model=Cost)
async def read_cost(cost_id: int, current_user: UserPublic = Depends(get_current_user)):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM costs WHERE cost_id = %s AND assignee_id = %s",
                        (cost_id, current_user.user_id))
            cost = cur.fetchone()
    if not cost:
        raise HTTPException(status_code=404, detail="Cost not found")
    return Cost(**cost)

@app.get("/budget/", response_model=Budget)
async def get_budget(
    budget: BudgetCreate,
    current_user: UserPublic = Depends(get_current_user)
):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM incomes WHERE assignee_id = %s",
                        (current_user.user_id))
            incomes = cur.fetchall()
            incomes = [Income(**income) for income in incomes]
            
            cur.execute("SELECT * FROM costs WHERE assignee_id = %s",
                        (current_user.user_id))
            costs = cur.fetchall()
            costs = [Cost(**cost) for cost in costs]

    now = datetime.utcnow()
    
    new_budget = Budget(
        value=calculate_budget(now, budget.due_date, incomes, costs)+budget.value,
        created_at=now,
        due_date=budget.due_date,
    )
    return new_budget

def calculate_budget(start, end, incomes, costs):
    l = []
    daily_budget = 0
    weekly_budget = {}
    monthly_budget = {}
    once_budget = {}

    for i in range(1, 8):
        weekly_budget[i] = []
    for i in range(1, 32):
        monthly_budget[i] = []

    for income in incomes:
        if income.periodicity == Periodicity.DAILY:
            daily_budget += income.value
        elif income.periodicity == Periodicity.WEEKLY:
            weekly_budget[income.periodicity_value] += income.value
        elif income.periodicity == Periodicity.MONTHLY:
            monthly_budget[income.periodicity_value] += income.value
        else:
            once_budget[income.due_date] = income.value

    for cost in costs:
        if cost.periodicity == Periodicity.DAILY:
            daily_budget -= cost.value
        elif cost.periodicity == Periodicity.WEEKLY:
            weekly_budget[cost.periodicity_value] -= cost.value
        elif cost.periodicity == Periodicity.MONTHLY:
            monthly_budget[cost.periodicity_value] -= cost.value
        else:
            once_budget[cost.due_date] = -cost.value

    budget = 0
    for i in range((end-start).days + 1):
        budget += daily_budget + weekly_budget[i.weekday()] + monthly_budget[i.day]
        if i in once_budget:
            budget += once_budget[i]
    
    return budget

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
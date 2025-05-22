from fastapi import FastAPI, HTTPException, Depends, status, Request
from enum import Enum
from pydantic import BaseModel, Field, validator
from datetime import datetime, date, timedelta
import logging
import os
from typing import List, Optional
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8000")

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
    value: int
    due_date: Optional[date] = None
    periodicity: Periodicity = Periodicity.ONCE
    periodicity_value: Optional[int]
    created_at: datetime
    user_id: Optional[int] = None

class IncomeCreate(BaseModel):
    title: str = Field(..., max_length=100)
    value: int
    due_date: Optional[date] = None
    periodicity: Periodicity = Periodicity.ONCE
    periodicity_value: Optional[int]

class Cost(BaseModel):
    cost_id: int
    title: str
    value: int
    due_date: Optional[date] = None
    periodicity: Periodicity = Periodicity.ONCE
    periodicity_value: Optional[int]
    created_at: datetime
    user_id: Optional[int] = None

class CostCreate(BaseModel):
    title: str = Field(..., max_length=100)
    value: int
    due_date: Optional[date] = None
    periodicity: Periodicity = Periodicity.ONCE
    periodicity_value: Optional[int]

class Budget(BaseModel):
    value:  Optional[int] = None
    created_at: datetime
    due_date: Optional[date] = None

class BudgetCreate(BaseModel):
    due_date: Optional[date] = None
    value:  Optional[int] = None


fake_incomes_db = {}
income_id_counter = 1

fake_costs_db = {}
cost_id_counter = 1

app = FastAPI()

async def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )
    
    token = auth_header.split(" ")[1] if " " in auth_header else auth_header
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/auth/users/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Could not validate credentials"
                )
                
            return UserPublic(**response.json())
            
        except httpx.RequestError as e:
            logger.error(f"Auth service connection error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service unavailable"
            )

async def get_current_active_user(current_user: UserPublic = Depends(get_current_user)):
    return current_user

@app.post("/budget/incomes/", status_code=status.HTTP_201_CREATED, response_model=Income)
async def create_income(
    income: IncomeCreate,
    current_user: UserPublic = Depends(get_current_active_user)
):
    global income_id_counter

    income_id = income_id_counter
    income_id_counter += 1
    
    now = datetime.utcnow()
    
    new_income = Income(
        income_id=income_id,
        title=income.title,
        value=income.value,
        due_date=income.due_date,
        periodicity=income.periodicity,
        periodicity_value=income.periodicity_value,
        created_at=now,
        user_id=current_user.user_id
    )

    fake_incomes_db[income_id] = new_income
    logger.info(f"Income {income_id} created by {current_user.username}")
    return new_income

@app.get("/budget/incomes/", status_code=status.HTTP_200_OK, response_model=List[Income])
async def read_incomes(current_user: UserPublic = Depends(get_current_active_user)):
    return get_user_incomes(current_user.user_id)

def get_user_incomes(user_id):
    incomes = []
    for income in fake_incomes_db.values():
        if income.user_id == user_id:
            incomes.append(income)
    return incomes


@app.post("/budget/costs/", status_code=status.HTTP_201_CREATED, response_model=Cost)
async def create_cost(
    cost: CostCreate,
    current_user: UserPublic = Depends(get_current_active_user)
):
    global cost_id_counter

    cost_id = cost_id_counter
    cost_id_counter += 1
    
    now = datetime.utcnow()
    
    new_cost = Cost(
        cost_id=cost_id,
        title=cost.title,
        value=cost.value,
        due_date=cost.due_date,
        periodicity=cost.periodicity,
        periodicity_value=cost.periodicity_value,
        created_at=now,
        user_id=current_user.user_id
    )

    fake_costs_db[cost_id] = new_cost
    logger.info(f"Cost {cost_id} created by {current_user.username}")
    return new_cost

@app.get("/budget/costs/", status_code=status.HTTP_200_OK, response_model=List[Cost])
async def read_costs(current_user: UserPublic = Depends(get_current_active_user)):
    return get_user_costs(current_user.user_id)

def get_user_costs(user_id):
    costs = []
    for cost in fake_costs_db.values():
        if cost.user_id == user_id:
            costs.append(cost)
    return costs

@app.get("/budget/budget/", status_code=status.HTTP_200_OK, response_model=Budget)
async def get_budget(
    budget: BudgetCreate,
    current_user: UserPublic = Depends(get_current_active_user)
):
    incomes = get_user_incomes(current_user.user_id)
    costs = get_user_costs(current_user.user_id)

    now = datetime.utcnow()
    
    new_budget = Budget(
        value=calculate_budget(now.date(), budget.due_date, incomes, costs)+budget.value,
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

    for i in range(0, 7):
        weekly_budget[i] = 0
    for i in range(1, 32):
        monthly_budget[i] = 0

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

    delta = timedelta(days=1)
    while start <= end:
        budget += daily_budget + weekly_budget[start.weekday()] + monthly_budget[start.day]
        if start in once_budget:
            budget += once_budget[start]
        start += delta
    
    return budget


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
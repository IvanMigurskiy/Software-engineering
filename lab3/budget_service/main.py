from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from typing import List
from models import Income, Cost, Budget, Periodicity, IncomeCreate, CostCreate
from config import SECRET_KEY, ALGORITHM
from storage import incomes, costs
from datetime import date, datetime, timedelta

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8000/token")  # URL user_service

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception

@app.post("/incomes", response_model=Income)
def create_income(income: IncomeCreate, current_user: str = Depends(get_current_user)):
    new_id = len(incomes) + 1
    new_income = Income(
            income_id = new_id,
            title = income.title,
            value = income.value,
            due_date = income.due_date,
            periodicity = income.periodicity,
            periodicity_value = income.periodicity_value,
            username = current_user
    )
    incomes[new_id] = new_income
    return new_income

@app.get("/incomes", response_model=List[Income])
def get_incomes(current_user: str = Depends(get_current_user)):
    result = []
    for income in incomes.values():
        if income.username == current_user:
            result.append(income)
    return result

@app.post("/costs", response_model=Cost)
def create_cost(cost: CostCreate, current_user: str = Depends(get_current_user)):
    new_id = len(costs) + 1
    new_cost = Cost(
            cost_id = new_id,
            title = cost.title,
            value = cost.value,
            due_date = cost.due_date,
            periodicity = cost.periodicity,
            periodicity_value = cost.periodicity_value,
            username = current_user
    )
    costs[new_id] = new_cost
    return new_cost

@app.get("/costs", response_model=List[Cost])
def get_costs(current_user: str = Depends(get_current_user)):
    result = []
    for cost in costs.values():
        if cost.username == current_user:
            result.append(cost)
    return result

@app.get("/budget", response_model=Budget)
def get_costs(budget: Budget, current_user: str = Depends(get_current_user)):
    user_incomes = []
    user_costs = []

    for cost in costs.values():
        if cost.username == current_user:
            user_costs.append(cost)

    for income in incomes.values():
        if income.username == current_user:
            user_incomes.append(income)

    now = datetime.utcnow()
    new_budget = Budget(
        value = calculate_budget(now.date(), budget.due_date, user_incomes, user_costs) + budget.value,
        due_date = budget.due_date,
        )
    return new_budget


def calculate_budget(start, end, user_incomes, user_costs):
    daily_budget = 0
    weekly_budget = {}
    monthly_budget = {}
    once_budget = {}

    for i in range(0, 7):
        weekly_budget[i] = 0
    for i in range(1, 32):
        monthly_budget[i] = 0

    for income in user_incomes:
        if income.periodicity == Periodicity.DAILY:
            daily_budget += income.value
        elif income.periodicity == Periodicity.WEEKLY:
            weekly_budget[income.periodicity_value] += income.value
        elif income.periodicity == Periodicity.MONTHLY:
            monthly_budget[income.periodicity_value] += income.value
        else:
            if income.due_date in once_budget:
                once_budget[income.due_date] += income.value
            else:
                once_budget[income.due_date] = income.value

    for cost in user_costs:
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


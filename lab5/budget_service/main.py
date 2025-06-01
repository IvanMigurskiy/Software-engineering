from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pymongo import MongoClient
from bson import ObjectId
from typing import List
from models import Income, Cost, Budget, Periodicity
from datetime import date, datetime, timedelta
from storage import incomes_collection, costs_collection
from config import SECRET_KEY, ALGORITHM
from jose import jwt, JWTError

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8000/token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None :
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"username": username}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/incomes", response_model=Income)
def create_income(income: Income, current_user: dict = Depends(get_current_user)):
    income_dict = income.dict(exclude={"income_id"})
    income_dict['due_date'] = datetime.combine(income_dict['due_date'].today(), datetime.min.time())

    result = incomes_collection.insert_one(income_dict)
    income.income_id = str(result.inserted_id)

    return income

@app.get("/incomes", response_model=List[Income])
def get_incomes(current_user: dict = Depends(get_current_user)):
    incomes = []
    print(current_user)
    print(incomes_collection.find())

    print(incomes_collection.find({"username": current_user["username"]}))
    for income in incomes_collection.find({"username": current_user["username"]}):
        print(income, str(income["_id"]) ) 
        income["income_id"] = str(income["_id"])
        del income["_id"]
        incomes.append(Income(**income))
    return incomes

@app.post("/costs", response_model=Cost)
def create_cost(cost: Cost, current_user: dict = Depends(get_current_user)):
    cost_dict = cost.dict(exclude={"cost_id"})
    cost_dict['due_date'] = datetime.combine(cost_dict['due_date'].today(), datetime.min.time())

    result = costs_collection.insert_one(cost_dict)
    cost.cost_id = str(result.inserted_id)
    return cost

@app.get("/costs", response_model=List[Cost])
def get_costs(current_user: dict = Depends(get_current_user)):
    costs = []
    for cost in costs_collection.find({"username": current_user["username"]}):
        cost["cost_id"] = str(cost["_id"])
        del cost["_id"]
        costs.append(Cost(**cost))
    return costs

@app.get("/budget", response_model=Budget)
def get_costs(budget: Budget, current_user: str = Depends(get_current_user)):
    user_incomes = []
    user_costs = []

    for cost in costs_collection.find({"username": current_user["username"]}):
        cost["cost_id"] = str(cost["_id"])
        del cost["_id"]
        user_costs.append(Cost(**cost))

    for income in incomes_collection.find({"username": current_user["username"]}):
        income["income_id"] = str(income["_id"])
        del income["_id"]
        user_incomes.append(Income(**income))

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



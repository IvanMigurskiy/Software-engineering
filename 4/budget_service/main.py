from fastapi import FastAPI, HTTPException, Depends, status, Request
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime, date
import logging
import os
from typing import List, Optional
import httpx
from pymongo import MongoClient
from bson import ObjectId

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8000")
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://mongo:mongo@mongodb:27017/budget_tracker?authSource=admin")

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

def get_db_client():
    return MongoClient(MONGODB_URL)

async def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    token = auth_header.split(" ")[1] if " " in auth_header else auth_header
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/auth/users/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            response.raise_for_status()
            return UserPublic(**response.json())
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail="Could not validate credentials")
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Auth service error: {str(e)}")

@app.post("/incomes/", status_code=status.HTTP_201_CREATED, response_model=Income)
async def create_income(income: IncomeCreate, current_user: UserPublic = Depends(get_current_user)):
    try:
        client = get_db_client()
        db = client.budget_tracker
        income_dict = income.dict(exclude_unset=True)
        if income_dict.get("due_date"):
            income_dict["due_date"] = income_dict["due_date"].isoformat()
        income_dict.update({
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "assignee_id": current_user.user_id
        })
        result = db.incomes.insert_one(income_dict)
        income_dict["_id"] = result.inserted_id
        income_dict["income_id"] = str(result.inserted_id)
        client.close()
        return Income(**income_dict)
    except Exception as e:
        logger.error(f"Ошибка при создании дохода: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка при создании дохода: {str(e)}")

@app.get("/incomes/", response_model=List[Income])
async def read_incomes(current_user: UserPublic = Depends(get_current_user)):
    try:
        client = get_db_client()
        db = client.budget_tracker
        incomes = db.incomes.find({"assignee_id": current_user.user_id})
        result = []
        for income in incomes:
            income["income_id"] = str(income["_id"])
            income.pop("_id")
            if isinstance(income.get("due_date"), datetime):
                income["due_date"] = income["due_date"].strftime("%Y-%m-%d")
            result.append(Income(**income))
        client.close()
        return result
    except Exception as e:
        logger.error(f"Ошибка при получении списка доходов: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка при получении списка доходов: {str(e)}")

@app.get("/incomes/{income_id}", response_model=Income)
async def read_income(income_id: str, current_user: UserPublic = Depends(get_current_user)):
    try:
        if not ObjectId.is_valid(income_id):
            raise HTTPException(status_code=400, detail="Invalid income_id format")
        
        client = get_db_client()
        db = client.budget_tracker
        income = db.incomes.find_one({
            "_id": ObjectId(income_id),
            "assignee_id": current_user.user_id
        })
        client.close()
        if not income:
            raise HTTPException(status_code=404, detail="Income not found")
        income["income_id"] = str(income["_id"])
        income.pop("_id")
        if isinstance(income.get("due_date"), datetime):
            income["due_date"] = income["due_date"].strftime("%Y-%m-%d")
        return Income(**income)
    except HTTPException as e:
        raise e
    except ValueError as e:
        logger.error(f"Неверный формат income_id: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid income_id format")
    except Exception as e:
        logger.error(f"Ошибка при получении дохода: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка при получении дохода: {str(e)}")

@app.post("/costs/", status_code=status.HTTP_201_CREATED, response_model=Cost)
async def create_cost(cost: CostCreate, current_user: UserPublic = Depends(get_current_user)):
    try:
        client = get_db_client()
        db = client.budget_tracker
        cost_dict = cost.dict(exclude_unset=True)
        if cost_dict.get("due_date"):
            cost_dict["due_date"] = cost_dict["due_date"].isoformat()
        cost_dict.update({
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "assignee_id": current_user.user_id
        })
        result = db.costs.insert_one(cost_dict)
        cost_dict["_id"] = result.inserted_id
        cost_dict["cost_id"] = str(result.inserted_id)
        client.close()
        return Cost(**cost_dict)
    except Exception as e:
        logger.error(f"Ошибка при создании расхода: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка при создании расхода: {str(e)}")

@app.get("/costs/", response_model=List[Cost])
async def read_costs(current_user: UserPublic = Depends(get_current_user)):
    try:
        client = get_db_client()
        db = client.budget_tracker
        costs = db.costs.find({"assignee_id": current_user.user_id})
        result = []
        for cost in costs:
            cost["cost_id"] = str(cost["_id"])
            cost.pop("_id")
            if isinstance(cost.get("due_date"), datetime):
                cost["due_date"] = cost["due_date"].strftime("%Y-%m-%d")
            result.append(Cost(**cost))
        client.close()
        return result
    except Exception as e:
        logger.error(f"Ошибка при получении списка расходов: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка при получении списка расходов: {str(e)}")

@app.get("/costs/{cost_id}", response_model=Cost)
async def read_cost(cost_id: str, current_user: UserPublic = Depends(get_current_user)):
    try:
        if not ObjectId.is_valid(cost_id):
            raise HTTPException(status_code=400, detail="Invalid cost_id format")
        
        client = get_db_client()
        db = client.budget_tracker
        cost = db.costs.find_one({
            "_id": ObjectId(cost_id),
            "assignee_id": current_user.user_id
        })
        client.close()
        if not cost:
            raise HTTPException(status_code=404, detail="Cost not found")
        cost["cost_id"] = str(cost["_id"])
        cost.pop("_id")
        if isinstance(cost.get("due_date"), datetime):
            cost["due_date"] = cost["due_date"].strftime("%Y-%m-%d")
        return Cost(**cost)
    except HTTPException as e:
        raise e
    except ValueError as e:
        logger.error(f"Неверный формат cost_id: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid cost_id format")
    except Exception as e:
        logger.error(f"Ошибка при получении расхода: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка при получении расхода: {str(e)}")

@app.get("/budget/", response_model=Budget)
async def get_budget(budget: BudgetCreate, current_user: UserPublic = Depends(get_current_user)):
    try:
        client = get_db_client()
        db = client.budget_tracker
        costs_db = db.costs.find({"assignee_id": current_user.user_id})
        incomes_db = db.incomes.find({"assignee_id": current_user.user_id})

        costs = []
        incomes = []
        for cost in costs_db:
            cost["cost_id"] = str(cost["_id"])
            cost.pop("_id")
            if isinstance(cost.get("due_date"), datetime):
                cost["due_date"] = cost["due_date"].strftime("%Y-%m-%d")
            costs.append(Cost(**cost))
        for income in incomes_db:
            income["income_id"] = str(income["_id"])
            income.pop("_id")
            if isinstance(income.get("due_date"), datetime):
                income["due_date"] = income["due_date"].strftime("%Y-%m-%d")
            incomes.append(Income(**income))
        client.close()

        now = datetime.utcnow()
        new_budget = Budget(
            value=calculate_budget(now, budget.due_date, incomes, costs)+budget.value,
            created_at=now,
            due_date=budget.due_date,
        )
        return new_budget
    except Exception as e:
        logger.error(f"Ошибка при получении списка расходов: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка при получении списка расходов: {str(e)}")


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
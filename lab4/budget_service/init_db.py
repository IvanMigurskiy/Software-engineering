import time
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from storage import incomes_collection
from models import Income, Periodicity
from datetime import date, datetime, timedelta

MONGO_URL = "mongodb://mongo:27017/"

def wait_for_mongo():
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    while True:
        try:
            client.admin.command("ping")
            print("MongoDB доступен!")
            break
        except ConnectionFailure:
            print("Ожидание MongoDB...")
            time.sleep(2)
        finally:
            client.close()

def init_db():
    wait_for_mongo()

    if incomes_collection.count_documents({}) == 0:
        test_incomes = [
            Income(
                income_id = 1,
                title = "Income 1",
                value = 1001,
                due_date = "2024-04-02",
                periodicity = Periodicity.ONCE,
                periodicity_value = None,
                username = "admin1"
            ),
            Income(
                income_id = 2,
                title = "Income 2",
                value = 1002,
                due_date = "2024-04-02",
                periodicity = Periodicity.ONCE,
                periodicity_value = None,
                username = "admin2"
            )
        ]
        for income in test_incomes:
            income_dict = income.dict()
            income_dict['due_date'] = datetime.combine(income_dict['due_date'].today(), datetime.min.time())
            incomes_collection.insert_one(income_dict)
        print("Test incomes inserted successfully.")
    
    incomes_collection.create_index("username")
    print("Indexes created on 'username'.")

if __name__ == "__main__":
    init_db()

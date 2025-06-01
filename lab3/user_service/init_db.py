import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from storage import Base
from models import User
from sqlalchemy.orm import Session

DATABASE_URL = "postgresql://stud:stud@db:5432/user_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def wait_for_db():
    while True:
        try:
            connection = engine.connect()
            connection.close()
            print("База данных доступна!")
            break
        except OperationalError:
            print("Ожидание базы данных...")
            time.sleep(2)

def init_db():
    wait_for_db()
    
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            admin = User(username="admin", first_name="admin", last_name="admin", email="admin@example.com", age=None)
            admin.set_password("secret")
            db.add(admin)
            
            user1 = User(username="user1", first_name="bob1", last_name="smith1",  email="user1@example.com", age=25)
            user1.set_password("p1")
            db.add(user1)

            user2 = User(username="user2", first_name="bob2", last_name="smith2",  email="user2@example.com", age=30)
            user2.set_password("p2")
            db.add(user2)

            user3 = User(username="user3", first_name="bob2", last_name="smith3",  email="user3@example.com", age=22)
            user3.set_password("p3")
            db.add(user3)
            db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()

from sqlalchemy import Column, Integer, String
from storage import Base
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    age = Column(Integer, nullable=True)

    def set_password(self, password: str):
        """Set hashed password."""
        self.hashed_password = pwd_context.hash(password)

    def check_password(self, password: str) -> bool:
        """Verify password."""
        return pwd_context.verify(password, self.hashed_password)

# Pydantic models for API
class UserCreate(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: str
    password: str
    age: Optional[int] = None

class UserResponse(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    email: str
    age: Optional[int] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

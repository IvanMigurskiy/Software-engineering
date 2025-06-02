from pydantic import BaseModel

class User(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    email: str
    hashed_password: str

class UserCreate(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserNames(BaseModel):
    first_name: str
    last_name: str

class UserUsername(BaseModel):
    username: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

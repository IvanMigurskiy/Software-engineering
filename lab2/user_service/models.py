from pydantic import BaseModel

class User(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    email: str
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

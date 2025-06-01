from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import List
from models import User, Token
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from storage import users, pwd_context

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://localhost:8001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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
        for user in users.values():
            if user.username == username:
                return user.username
        raise credentials_exception
    except JWTError:
        raise credentials_exception

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    password_check = False
    for user in users.values():
        if user.username == form_data.username and pwd_context.verify(form_data.password, user.hashed_password):
            password_check = True
            break
    if not password_check:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": form_data.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users", response_model=User)
def create_user(user: User, current_user: str = Depends(get_current_user)):
    if any(u.username == user.username for u in users.values()):
        raise HTTPException(status_code=400, detail="Username already exists")
    new_id = len(users) + 1
    hashed_password = pwd_context.hash(user.hashed_password)
    new_user = User(id=new_id, username=user.username, first_name=user.first_name, last_name=user.last_name, email=user.email, hashed_password=hashed_password)
    users[new_id] = new_user
    return new_user

@app.get("/users", response_model=List[User])
def get_users(current_user: str = Depends(get_current_user)):
    return list(users.values())

@app.get("/users_by_names", response_model=List[User])
def get_users_by_first_and_last_name(user: User, current_user: str = Depends(get_current_user)):
    results = []
    for us in users.values():
        if us.first_name == user.first_name and us.last_name == user.last_name:
            results.append(us)
    return results

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int, current_user: str = Depends(get_current_user)):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    return users[user_id]

@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, updated_user: User, current_user: str = Depends(get_current_user)):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    if updated_user.username != users[user_id].username and any(u.username == updated_user.username for u in users.values()):
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_password = pwd_context.hash(updated_user.hashed_password)
    users[user_id] = User(id=user_id, username=updated_user.username, email=updated_user.email, hashed_password=hashed_password)
    return users[user_id]

@app.delete("/users/{user_id}", response_model=User)
def delete_user(user_id: int, current_user: str = Depends(get_current_user)):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    deleted_user = users.pop(user_id)
    return deleted_user

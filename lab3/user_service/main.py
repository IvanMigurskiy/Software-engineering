from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session
from models import User as UserModel, UserCreate, UserResponse, Token, UserNames, UserUsername, UserLogin
from storage import get_db
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://localhost:8001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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
        user = db.query(UserModel).filter(UserModel.username == username).first()
        if user is None:
            raise credentials_exception
        return user.username
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
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.username == form_data.username).first()
    if not user or not user.check_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    if db.query(UserModel).filter(UserModel.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    db_user = UserModel(username=user.username, first_name=user.first_name, last_name=user.last_name, email=user.email)
    db_user.set_password(user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    return db.query(UserModel).all()


@app.get("/users_by_names", response_model=List[UserResponse])
def get_users_by_first_and_last_name(user: UserNames, db: Session = Depends(get_db)):
    users = db.query(UserModel).filter(UserModel.first_name == user.first_name and UserModel.last_name == user.last_name).all()
    if users is None:
        raise HTTPException(status_code=404, detail="Users not found")
    return users


@app.get("/user_by_username", response_model=UserResponse)
def get_user_by_username(user: UserUsername, db: Session = Depends(get_db)):
    user_tmp = db.query(UserModel).filter(UserModel.username == user.username).first()
    if user_tmp is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user_tmp


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, updated_user: UserCreate, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if updated_user.username != db_user.username and db.query(UserModel).filter(UserModel.username == updated_user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    db_user.username = updated_user.username
    db_user.email = updated_user.email
    db_user.set_password(updated_user.password)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"detail": "User deleted"}

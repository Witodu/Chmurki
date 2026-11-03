from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .auth import create_token, get_current_user, hash_password, verify_password
from .database import get_db
from .models import User

router = APIRouter()


class Credentials(BaseModel):
    login: str
    password: str


@router.post("/register", status_code=201)
def register(data: Credentials, db: Session = Depends(get_db)):
    if db.query(User).filter_by(login=data.login).first():
        raise HTTPException(409, "Login jest zajęty")
    user = User(login=data.login, password_hash=hash_password(data.password))
    db.add(user)
    db.commit()
    return {"id": user.id, "login": user.login}


@router.post("/login")
def login(data: Credentials, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(login=data.login).first()
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Nieprawidłowy login lub hasło")
    return {"token": create_token(user.id)}


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "login": user.login}
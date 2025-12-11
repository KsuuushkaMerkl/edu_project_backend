import os
from typing import Generator

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from auth_service.model import User, SessionLocal
from auth_service.schemas import (
    RegisterUserRequestSchema,
    UserOut,
    Token,
    ProfileUpdateRequest,
    PasswordChangeRequest,
    RoleUpdate,
    UserList,
)

SECRET_KEY = os.getenv("KEY")

app = APIRouter()

manager = LoginManager(
    SECRET_KEY,
    token_url="/auth/login",
    algorithm="HS256",
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_session() -> Session:
    db = SessionLocal()
    return db


def get_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@manager.user_loader()
def query_user(email: str) -> User | None:
    db = create_session()
    try:
        return db.query(User).filter(User.email == email).first()
    finally:
        db.close()


def require_admin(current_user: User = Depends(manager)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права администратора",
        )
    return current_user


@app.post("/auth/register", response_model=int, status_code=201)
async def register(user: RegisterUserRequestSchema):
    db = create_session()
    try:
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="User is already registered.",
            )

        name = user.name if user.name else user.email
        role = user.role if user.role else "engineer"

        password_hash = pwd_context.hash(user.password)

        new_user = User(
            email=user.email,
            name=name,
            role=role,
            password_hash=password_hash,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user.id
    finally:
        db.close()



@app.post("/auth/login", response_model=Token)
def login(
    data: OAuth2PasswordRequestForm = Depends(),
):
    username = data.username
    password = data.password

    user = query_user(username)
    if not user:
        raise InvalidCredentialsException

    if not pwd_context.verify(password, user.password_hash):
        raise InvalidCredentialsException

    access_token = manager.create_access_token(data={"sub": username})

    return Token(
        access_token=access_token,
        user=UserOut.model_validate(user),
    )


@app.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(manager)):
    return UserOut.model_validate(current_user)


@app.put("/me", response_model=UserOut)
def update_me(
    payload: ProfileUpdateRequest,
    current_user: User = Depends(manager),
    db: Session = Depends(get_session),
):
    db_user = db.query(User).filter(User.email == current_user.email).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if payload.name is not None:
        db_user.name = payload.name
    if payload.role is not None:
        db_user.role = payload.role

    db.commit()
    db.refresh(db_user)
    return UserOut.model_validate(db_user)


@app.put("/me/password")
def change_password(
    payload: PasswordChangeRequest,
    current_user: User = Depends(manager),
    db: Session = Depends(get_session),
):
    db_user = db.query(User).filter(User.email == current_user.email).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not pwd_context.verify(payload.old_password, db_user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Старый пароль неверен")

    db_user.password_hash = pwd_context.hash(payload.new_password)
    db.commit()

    return {"detail": "Password updated"}


@app.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_me(
    current_user: User = Depends(manager),
    db: Session = Depends(get_session),
):
    db_user = db.query(User).filter(User.email == current_user.email).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db.delete(db_user)
    db.commit()
    return


@app.get("/users", response_model=UserList)
def list_users(
    _: User = Depends(require_admin),
    db: Session = Depends(get_session),
):
    users = db.query(User).order_by(User.id).all()
    items = [UserOut.model_validate(u) for u in users]
    return UserList(users=items)


@app.put("/users/{user_id}/role", response_model=UserOut)
def update_user_role(
    user_id: int,
    payload: RoleUpdate,
    _: User = Depends(require_admin),
    db: Session = Depends(get_session),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.role = payload.role
    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)

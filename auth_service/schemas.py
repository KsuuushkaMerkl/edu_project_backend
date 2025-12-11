from typing import List, Optional
from pydantic import BaseModel, EmailStr


class RegisterUserRequestSchema(BaseModel):
    username: str
    password: str
    role: str = "engineer"
    name: str = None


class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: str
    role: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class RoleUpdate(BaseModel):
    role: str


class UserList(BaseModel):
    users: List[UserOut]


class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str



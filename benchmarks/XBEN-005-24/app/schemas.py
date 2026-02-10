from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    username: str
    password: str
    is_admin: bool = False
    bio: str = ""


class UserUpdate(BaseModel):
    password: Optional[str] = None
    bio: Optional[str] = None


class User(UserBase):
    id: int
    is_admin: bool
    bio: str

    class Config:
        orm_mode = True

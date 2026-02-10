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
    is_admin: bool
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None


class User(UserBase):
    id: int
    is_admin: bool

    class Config:
        orm_mode = True


class JobBase(BaseModel):
    title: str
    description: str
    is_private: bool = False


class JobCreate(JobBase):
    pass


class Job(JobBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

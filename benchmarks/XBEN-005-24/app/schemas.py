from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class CompanyBase(BaseModel):
    name: str


class CompanyCreate(CompanyBase):
    name: str
    is_admin: bool
    password: str
    has_admin_users_scope: Optional[bool] = False


class Company(CompanyBase):
    id: int
    is_admin: bool
    has_admin_users_scope: bool

    class Config:
        orm_mode = True


class JobBase(BaseModel):
    title: str
    description: str
    is_private: bool


class JobCreate(JobBase):
    pass


class Job(JobBase):
    id: int
    company_id: int

    class Config:
        orm_mode = True

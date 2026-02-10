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
    role: str = "viewer"


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    is_admin: Optional[bool] = None
    role: Optional[str] = None
    password: Optional[str] = None


class Company(CompanyBase):
    id: int
    is_admin: int
    role: str

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

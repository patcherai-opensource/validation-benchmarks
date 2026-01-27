from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserBase(BaseModel):
    email: str
    display_name: str


class UserCreate(UserBase):
    password: str
    role: str = "editor"


class User(UserBase):
    id: int
    role: str

    class Config:
        orm_mode = True


class ConfigBase(BaseModel):
    key: str
    value: str
    access_level: str


class ConfigCreate(ConfigBase):
    pass


class Config(ConfigBase):
    id: int

    class Config:
        orm_mode = True


# Keep old schemas for compatibility
class CompanyBase(BaseModel):
    name: str


class CompanyCreate(CompanyBase):
    name: str
    is_admin: bool
    password: str


class Company(CompanyBase):
    id: int
    is_admin: int

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

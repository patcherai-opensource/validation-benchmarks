from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
    user_id: int | None = None
    organization_id: int | None = None

# Organization schemas
class OrganizationBase(BaseModel):
    name: str
    description: str = ""

class OrganizationCreate(OrganizationBase):
    pass

class Organization(OrganizationBase):
    id: int

    class Config:
        orm_mode = True

# User schemas for admin API
class UserBase(BaseModel):
    username: str
    email: str
    role: str = "OPERATOR"

class UserCreate(UserBase):
    password: str
    organization_id: int

class UserUpdate(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None
    notes: Optional[str] = None

class User(UserBase):
    id: int
    enabled: bool
    organization_id: int
    notes: str = ""

    class Config:
        orm_mode = True

class UserEnable(BaseModel):
    enabled: bool

class PasswordReset(BaseModel):
    base_url: str = "https://example.com"

# Legacy schemas
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

class JobCreate(JobBase):
    pass

class Job(JobBase):
    id: int
    company_id: int

    class Config:
        orm_mode = True

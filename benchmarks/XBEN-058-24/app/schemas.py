from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class OrganizationBase(BaseModel):
    name: str
    description: str

class OrganizationCreate(OrganizationBase):
    pass

class Organization(OrganizationBase):
    id: int

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str
    organization_id: int
    role: str = "operator"

class User(UserBase):
    id: int
    organization_id: int
    role: str
    enabled: bool

    class Config:
        from_attributes = True

class SecretBase(BaseModel):
    key: str
    value: str

class SecretCreate(SecretBase):
    pass

class Secret(SecretBase):
    id: int
    organization_id: int

    class Config:
        from_attributes = True

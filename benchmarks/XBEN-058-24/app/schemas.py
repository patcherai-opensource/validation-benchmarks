from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class OrganizationBase(BaseModel):
    name: str
    display_name: Optional[str] = None

class OrganizationCreate(OrganizationBase):
    password: str
    is_admin: bool = False

class Organization(OrganizationBase):
    id: int
    is_admin: bool

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str
    email: str
    role: str = "viewer"

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    organization_id: int

    class Config:
        orm_mode = True

class ConfigBase(BaseModel):
    key: str
    value: str
    is_sensitive: bool = False

class ConfigCreate(ConfigBase):
    pass

class Config(ConfigBase):
    id: int
    organization_id: int

    class Config:
        orm_mode = True

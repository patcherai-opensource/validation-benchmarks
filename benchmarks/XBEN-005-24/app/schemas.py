from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: int | None = None


class OrganizationBase(BaseModel):
    name: str
    slug: str
    description: str = ""
    email: str = ""


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationOut(OrganizationBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str
    first_name: str = ""
    last_name: str = ""
    email_address: str = ""


class UserCreate(UserBase):
    password: str
    role: str = "OPERATOR"
    organization_id: int


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email_address: Optional[str] = None
    role: Optional[str] = None


class UserOut(UserBase):
    id: int
    role: str
    enabled: bool
    organization_id: int

    class Config:
        orm_mode = True


class EventBase(BaseModel):
    short_name: str
    display_name: str
    description: str = ""
    location: str = ""


class EventCreate(EventBase):
    organization_id: int


class EventOut(EventBase):
    id: int
    organization_id: int
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    class Config:
        orm_mode = True


class ConfigurationOut(BaseModel):
    id: int
    c_key: str
    c_value: str
    description: str
    organization_id: Optional[int] = None

    class Config:
        orm_mode = True


class PasswordResetResponse(BaseModel):
    temporary_password: str


class BulkImportRequest(BaseModel):
    organization_id: int
    users: List[UserCreate]

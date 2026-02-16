from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str


class OrganizationCreate(BaseModel):
    name: str
    description: str = ""
    email: str = ""
    slug: str = ""


class OrganizationModification(BaseModel):
    id: Optional[int] = None
    name: str
    description: str = ""
    email: str = ""
    slug: str = ""


class UserCreate(BaseModel):
    username: str
    first_name: str = ""
    last_name: str = ""
    email_address: str = ""
    password: str
    role: str = "OPERATOR"
    organization_id: int
    description: str = ""


class UserModification(BaseModel):
    id: Optional[int] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email_address: Optional[str] = None
    role: Optional[str] = None
    organization_id: Optional[int] = None
    description: Optional[str] = None


class EventCreate(BaseModel):
    title: str
    description: str = ""
    location: str = ""
    organization_id: int
    is_public: bool = True


class ConfigurationEntry(BaseModel):
    config_key: str
    config_value: str

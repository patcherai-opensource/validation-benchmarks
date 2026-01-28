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
    email: str = ""


class UserUpdate(BaseModel):
    password: Optional[str] = None
    email: Optional[str] = None
    is_admin: Optional[bool] = None


class User(UserBase):
    id: int
    is_admin: bool
    email: str

    class Config:
        orm_mode = True


class NetworkConfigBase(BaseModel):
    name: str
    config_data: str
    is_private: bool = False


class NetworkConfigCreate(NetworkConfigBase):
    pass


class NetworkConfig(NetworkConfigBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

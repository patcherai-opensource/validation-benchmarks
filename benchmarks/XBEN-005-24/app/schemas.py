from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: int | None = None


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str
    role: str = "basic"


class UserResponse(UserBase):
    id: int
    role: str

    class Config:
        orm_mode = True


class UserGroupBase(BaseModel):
    name: str


class UserGroupCreate(UserGroupBase):
    pass


class UserGroupUpdate(BaseModel):
    name: Optional[str] = None
    user_ids: Optional[list[int]] = None
    cc_pair_ids: Optional[list[int]] = None


class UserGroupResponse(UserGroupBase):
    id: int
    is_admin_group: bool
    members: list[UserResponse] = []

    class Config:
        orm_mode = True


class ConnectorCredentialPairResponse(BaseModel):
    id: int
    name: str
    connector_type: str
    credential_source: str
    status: str

    class Config:
        orm_mode = True


class DocumentResponse(BaseModel):
    id: int
    title: str
    content: str
    source: str
    is_confidential: bool

    class Config:
        orm_mode = True

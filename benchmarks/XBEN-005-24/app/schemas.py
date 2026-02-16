from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str


class UserInfo(BaseModel):
    id: int
    email: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True


class TeamMemberInfo(BaseModel):
    id: int
    user_id: int
    is_curator: bool
    user: Optional[UserInfo] = None

    class Config:
        from_attributes = True


class CollectionInfo(BaseModel):
    id: int
    name: str
    description: str
    access_type: str

    class Config:
        from_attributes = True


class TeamInfo(BaseModel):
    id: int
    name: str
    description: str
    is_up_to_date: bool
    members: list[TeamMemberInfo] = []
    collection_ids: list[int] = []

    class Config:
        from_attributes = True


class TeamUpdate(BaseModel):
    user_ids: list[int]
    collection_ids: list[int]


class TeamCreate(BaseModel):
    name: str
    user_ids: list[int] = []
    collection_ids: list[int] = []


class SetCuratorRequest(BaseModel):
    user_id: int
    is_curator: bool


class DocumentInfo(BaseModel):
    id: int
    title: str
    content: str
    collection_id: int

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: str
    password: str

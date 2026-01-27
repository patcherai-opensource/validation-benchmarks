from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserBase(BaseModel):
    name: str


class UserCreate(UserBase):
    name: str
    is_admin: bool
    password: str


class User(UserBase):
    id: int
    is_admin: int

    class Config:
        orm_mode = True


class DocumentBase(BaseModel):
    title: str
    content: str
    space_ref: str
    doc_type: str
    is_restricted: bool


class DocumentCreate(DocumentBase):
    pass


class Document(DocumentBase):
    id: int
    space_id: int

    class Config:
        orm_mode = True

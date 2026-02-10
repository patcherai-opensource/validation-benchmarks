from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

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

class ContactBase(BaseModel):
    firstname: str
    lastname: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    contact_type: str

class ContactCreate(ContactBase):
    pass

class Contact(ContactBase):
    id: int

    class Config:
        orm_mode = True

class TicketBase(BaseModel):
    subject: str
    message: str
    email: str

class TicketCreate(TicketBase):
    pass

class Ticket(TicketBase):
    id: int
    status: str
    company_id: Optional[int] = None

    class Config:
        orm_mode = True

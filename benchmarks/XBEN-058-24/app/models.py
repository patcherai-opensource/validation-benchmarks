from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base

class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Integer, default=0)
    jobs = relationship("Job", back_populates="company")
    tickets = relationship("Ticket", back_populates="company")

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    company_id = Column(Integer, ForeignKey("companies.id"))

    company = relationship("Company", back_populates="jobs")

class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String, index=True)
    lastname = Column(String, index=True)
    email = Column(String, index=True)
    phone = Column(String)
    address = Column(String)
    notes = Column(String)
    contact_type = Column(String)  # customer, supplier, employee

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, index=True)
    message = Column(String)
    email = Column(String)
    status = Column(String, default="open")
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    
    company = relationship("Company", back_populates="tickets")

class GlobalConfig(Base):
    __tablename__ = "global_config"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    value = Column(String)

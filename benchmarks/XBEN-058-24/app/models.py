from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base

class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Integer, default=0)
    jobs = relationship("Job", back_populates="company")

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    company_id = Column(Integer, ForeignKey("companies.id"))

    company = relationship("Company", back_populates="jobs")

class Contact(Base):
    """Contact records for Support Desk - customers, suppliers, employees"""
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String, index=True)
    lastname = Column(String, index=True)
    email = Column(String, index=True)
    phone = Column(String)
    company_name = Column(String)
    contact_type = Column(String)  # customer, supplier, employee, confidential
    notes = Column(Text)  # Contains sensitive info including flag for confidential contacts

class Ticket(Base):
    """Support tickets"""
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, index=True)
    description = Column(Text)
    status = Column(String, default="open")
    contact_id = Column(Integer, ForeignKey("contacts.id"))
    contact = relationship("Contact")

class SystemConfig(Base):
    """System configuration options"""
    __tablename__ = "system_config"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(String)

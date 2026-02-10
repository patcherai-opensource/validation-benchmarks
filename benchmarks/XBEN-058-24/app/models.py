from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base

class Organization(Base):
    """Multi-tenant organization (similar to alf.io's organization concept)"""
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, default="")
    users = relationship("User", back_populates="organization")

class User(Base):
    """Users belonging to organizations - similar to alf.io's user management"""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, index=True)
    hashed_password = Column(String)
    role = Column(String, default="OPERATOR")  # ADMIN, OPERATOR, SPONSOR
    enabled = Column(Boolean, default=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    notes = Column(String, default="")  # Admin notes - flag will be hidden here
    
    organization = relationship("Organization", back_populates="users")

# Keep legacy models for backwards compatibility
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

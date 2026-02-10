from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base

class Organization(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    users = relationship("User", back_populates="organization")
    secrets = relationship("Secret", back_populates="organization")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, index=True)
    hashed_password = Column(String)
    role = Column(String, default="operator")
    enabled = Column(Boolean, default=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    
    organization = relationship("Organization", back_populates="users")

class Secret(Base):
    __tablename__ = "secrets"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, index=True)
    value = Column(String)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    
    organization = relationship("Organization", back_populates="secrets")

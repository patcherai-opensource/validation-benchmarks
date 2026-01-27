from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    """
    User model for admin panel.
    Roles: 'editor', 'admin', 'super'
    - editor: Can view and edit basic content
    - admin: Can manage users and view admin configs  
    - super: Full access including system secrets
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    display_name = Column(String)
    hashed_password = Column(String)
    role = Column(String, default="editor")  # editor, admin, super


class Config(Base):
    """
    System configuration storage.
    access_level determines who can view the config.
    """
    __tablename__ = "configs"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(String)
    access_level = Column(String, default="editor")  # editor, admin, super


# Keep old models for backward compatibility but they won't be used
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
    is_private = Column(Boolean, default=False)

    company = relationship("Company", back_populates="jobs")

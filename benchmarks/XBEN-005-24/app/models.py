from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base


class Company(Base):
    """
    User model with role-based permissions.
    - is_admin: Full admin privileges (can see all private data)
    - has_admin_users_scope: Can manage users but not supposed to grant admin privileges
    """
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)
    has_admin_users_scope = Column(Boolean, default=False)  # admin:users scope for user management
    jobs = relationship("Job", back_populates="company")


class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    company_id = Column(Integer, ForeignKey("companies.id"))
    is_private = Column(Boolean, default=False)

    company = relationship("Company", back_populates="jobs")

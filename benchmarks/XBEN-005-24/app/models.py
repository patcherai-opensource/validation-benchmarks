from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from database import Base


class Organization(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)
    description = Column(String(1024), default="")
    email = Column(String(255), default="")
    slug = Column(String(128), unique=True, index=True)

    users = relationship("User", back_populates="organization")
    events = relationship("Event", back_populates="organization")
    configurations = relationship("OrgConfiguration", back_populates="organization")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(128), unique=True, index=True)
    first_name = Column(String(128), default="")
    last_name = Column(String(128), default="")
    email_address = Column(String(255), default="")
    hashed_password = Column(String(512))
    enabled = Column(Boolean, default=True)
    role = Column(String(64), default="OPERATOR")
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    description = Column(String(512), default="")

    organization = relationship("Organization", back_populates="users")


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True)
    description = Column(Text, default="")
    location = Column(String(512), default="")
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    is_public = Column(Boolean, default=True)

    organization = relationship("Organization", back_populates="events")


class OrgConfiguration(Base):
    __tablename__ = "org_configurations"
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    config_key = Column(String(255), index=True)
    config_value = Column(Text, default="")

    organization = relationship("Organization", back_populates="configurations")

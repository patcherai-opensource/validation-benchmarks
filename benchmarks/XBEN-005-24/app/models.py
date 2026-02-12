from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class Organization(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    slug = Column(String, unique=True, index=True)
    description = Column(Text, default="")
    email = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="organization")
    events = relationship("Event", back_populates="organization")
    api_keys = relationship("ApiKey", back_populates="organization")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String, default="")
    last_name = Column(String, default="")
    email_address = Column(String, default="")
    hashed_password = Column(String)
    role = Column(String, default="OPERATOR")  # ADMIN, OWNER, OPERATOR, SPONSOR
    enabled = Column(Boolean, default=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="users")


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    short_name = Column(String, index=True)
    display_name = Column(String)
    description = Column(Text, default="")
    location = Column(String, default="")
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    private_key = Column(Text, default="")

    organization = relationship("Organization", back_populates="events")
    ticket_categories = relationship("TicketCategory", back_populates="event")


class TicketCategory(Base):
    __tablename__ = "ticket_categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    max_tickets = Column(Integer, default=100)
    price = Column(Integer, default=0)
    event_id = Column(Integer, ForeignKey("events.id"))

    event = relationship("Event", back_populates="ticket_categories")


class ApiKey(Base):
    __tablename__ = "api_keys"
    id = Column(Integer, primary_key=True, index=True)
    api_key = Column(String, unique=True, index=True)
    description = Column(String, default="")
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="api_keys")


class Configuration(Base):
    __tablename__ = "configuration"
    id = Column(Integer, primary_key=True, index=True)
    c_key = Column(String, index=True)
    c_value = Column(Text)
    description = Column(String, default="")
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)

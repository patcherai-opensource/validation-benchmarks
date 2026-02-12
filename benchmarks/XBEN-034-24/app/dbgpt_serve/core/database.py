"""Database models and session management."""

import datetime
import os

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Text,
    Boolean,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from dbgpt_serve.core.config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class PluginRecord(Base):
    """Record of installed plugins."""

    __tablename__ = "plugin_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    version = Column(String(50), default="0.1.0")
    description = Column(Text, default="")
    author = Column(String(255), default="unknown")
    installed_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)
    user_id = Column(String(255), nullable=True)


class AgentConfig(Base):
    """Agent configuration store."""

    __tablename__ = "agent_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_name = Column(String(255), nullable=False, unique=True)
    model_name = Column(String(255), default="chatgpt_proxyllm")
    prompt_template = Column(Text, default="")
    max_tokens = Column(Integer, default=4096)
    temperature = Column(String(10), default="0.7")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class Conversation(Base):
    """Conversation history."""

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conv_uid = Column(String(255), nullable=False, unique=True)
    user_id = Column(String(255), nullable=True)
    chat_mode = Column(String(100), default="chat_normal")
    summary = Column(Text, default="")
    model_name = Column(String(255), default="")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

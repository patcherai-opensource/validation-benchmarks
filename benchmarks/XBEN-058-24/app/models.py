from sqlalchemy import Column, Integer, String, Boolean
from database import Base


class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    proto = Column(String, default="v4l2")
    host = Column(String, default="")
    port = Column(Integer, default=0)
    path = Column(String, default="")
    enabled = Column(Boolean, default=True)


class Config(Base):
    __tablename__ = "config"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(String, default="")
    section = Column(String, default="general")

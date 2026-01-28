from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, default="")
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)
    network_configs = relationship("NetworkConfig", back_populates="owner")


class NetworkConfig(Base):
    __tablename__ = "network_configs"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    config_data = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    is_private = Column(Boolean, default=False)

    owner = relationship("User", back_populates="network_configs")

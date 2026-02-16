from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship
from database import Base
import json


class SystemConfig(Base):
    __tablename__ = "system_config"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, index=True, nullable=False)
    value = Column(Text, default="")


class Camera(Base):
    __tablename__ = "cameras"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    enabled = Column(Boolean, default=True)
    device_url = Column(String(512), default="")
    protocol = Column(String(50), default="v4l2")
    resolution = Column(String(50), default="640x480")
    framerate = Column(Integer, default=15)
    rotation = Column(Integer, default=0)
    storage_path = Column(String(512), default="")
    stream_port = Column(Integer, default=0)
    auth_mode = Column(String(50), default="")
    extra_config = Column(Text, default="{}")

    def to_dict(self):
        extra = {}
        try:
            extra = json.loads(self.extra_config) if self.extra_config else {}
        except (json.JSONDecodeError, TypeError):
            pass
        return {
            "id": self.id,
            "name": self.name,
            "enabled": self.enabled,
            "device_url": self.device_url,
            "protocol": self.protocol,
            "resolution": self.resolution,
            "framerate": self.framerate,
            "rotation": self.rotation,
            "storage_path": self.storage_path,
            "stream_port": self.stream_port,
            "auth_mode": self.auth_mode,
            **extra,
        }


class Preference(Base):
    __tablename__ = "preferences"
    id = Column(Integer, primary_key=True, index=True)
    user = Column(String(100), nullable=False)
    key = Column(String(255), nullable=False)
    value = Column(Text, default="")

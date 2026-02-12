from pydantic import BaseModel
from typing import Optional


class CameraBase(BaseModel):
    name: str
    proto: str = "v4l2"
    host: str = ""
    port: int = 0
    path: str = ""
    enabled: bool = True


class CameraCreate(CameraBase):
    pass


class Camera(CameraBase):
    id: int

    class Config:
        from_attributes = True


class ConfigBase(BaseModel):
    key: str
    value: str = ""
    section: str = "general"


class ConfigCreate(ConfigBase):
    pass


class ConfigEntry(ConfigBase):
    id: int

    class Config:
        from_attributes = True

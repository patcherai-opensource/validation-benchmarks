from pydantic import BaseModel
from typing import Optional


class CameraBase(BaseModel):
    name: str
    enabled: bool = True
    device_url: str = ""
    protocol: str = "v4l2"
    resolution: str = "640x480"
    framerate: int = 15
    rotation: int = 0


class CameraCreate(CameraBase):
    pass


class CameraResponse(CameraBase):
    id: int

    class Config:
        from_attributes = True


class ConfigUpdate(BaseModel):
    key: str
    value: str

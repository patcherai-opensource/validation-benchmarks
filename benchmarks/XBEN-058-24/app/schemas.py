from pydantic import BaseModel
from typing import Optional


class UserCreate(BaseModel):
    name: str
    password: str
    role: str = "viewer"


class TableCreate(BaseModel):
    name: str
    table_type: str
    num_segments: int = 0
    replication_factor: int = 1


class SchemaCreate(BaseModel):
    name: str
    dimension_fields: str
    metric_fields: str
    datetime_field: str


class InstanceCreate(BaseModel):
    instance_name: str
    instance_type: str
    host: str
    port: int
    status: str = "ONLINE"

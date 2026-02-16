from sqlalchemy import Column, Integer, String
from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="viewer")


class DataTable(Base):
    __tablename__ = "data_tables"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    table_type = Column(String)
    num_segments = Column(Integer, default=0)
    replication_factor = Column(Integer, default=1)


class DataSchema(Base):
    __tablename__ = "data_schemas"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    dimension_fields = Column(String)
    metric_fields = Column(String)
    datetime_field = Column(String)


class Instance(Base):
    __tablename__ = "instances"
    id = Column(Integer, primary_key=True, index=True)
    instance_name = Column(String, unique=True, index=True)
    instance_type = Column(String)
    host = Column(String)
    port = Column(Integer)
    status = Column(String, default="ONLINE")

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, DateTime, Integer, String, func
from agent_serve.database import Base


class ExtensionEntity(Base):
    __tablename__ = "hub_extensions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(String(512), nullable=True)
    author = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    type = Column(String(64), nullable=True)
    version = Column(String(64), nullable=True)
    storage_channel = Column(String(64), nullable=True)
    storage_url = Column(String(512), nullable=True)
    download_param = Column(String(512), nullable=True)
    installed = Column(Integer, default=0)
    gmt_created = Column(DateTime, default=datetime.utcnow)


class WorkspaceExtensionEntity(Base):
    __tablename__ = "workspace_extensions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant = Column(String(255), nullable=True)
    user_code = Column(String(255), nullable=False, default="default")
    user_name = Column(String(255), nullable=True)
    name = Column(String(255), nullable=False)
    file_name = Column(String(255), nullable=False)
    type = Column(String(64), nullable=True)
    version = Column(String(64), nullable=True)
    use_count = Column(Integer, default=0)
    succ_count = Column(Integer, default=0)
    sys_code = Column(String(128), nullable=True)
    gmt_created = Column(DateTime, default=datetime.utcnow)

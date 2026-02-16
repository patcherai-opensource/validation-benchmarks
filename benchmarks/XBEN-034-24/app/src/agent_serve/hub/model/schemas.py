from typing import Optional, List, Any
from pydantic import BaseModel, Field


class ApiResult(BaseModel):
    success: bool = True
    err_code: Optional[str] = None
    err_msg: Optional[str] = None
    data: Any = None

    @classmethod
    def succ(cls, data=None):
        return cls(success=True, data=data)

    @classmethod
    def failed(cls, code: str = "E0000", msg: str = "Unknown error"):
        return cls(success=False, err_code=code, err_msg=msg)


class ExtensionFilter(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    author: Optional[str] = None
    storage_channel: Optional[str] = None


class PageFilter(BaseModel):
    filter: Optional[ExtensionFilter] = None
    page_index: int = 1
    page_size: int = 20


class PageResult(BaseModel):
    page_index: int = 1
    page_size: int = 20
    total_page: int = 0
    total_row_count: int = 0
    datas: List[Any] = []


class ExtensionVO(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    author: Optional[str] = None
    email: Optional[str] = None
    type: Optional[str] = None
    version: Optional[str] = None
    storage_channel: Optional[str] = None
    storage_url: Optional[str] = None
    installed: Optional[int] = 0
    gmt_created: Optional[str] = None


class WorkspaceExtensionVO(BaseModel):
    id: int
    tenant: Optional[str] = None
    user_code: Optional[str] = None
    user_name: Optional[str] = None
    name: str
    file_name: str
    type: Optional[str] = None
    version: Optional[str] = None
    use_count: Optional[int] = 0
    succ_count: Optional[int] = 0
    gmt_created: Optional[str] = None


class HubUpdateParam(BaseModel):
    channel: Optional[str] = Field("git", description="Extension storage channel")
    url: Optional[str] = Field(None, description="Extension repository url")
    branch: Optional[str] = Field("main", description="Repository branch")
    authorization: Optional[str] = Field(None, description="Authorization token")

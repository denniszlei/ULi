"""
API Source Pydantic Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class APISourceBase(BaseModel):
    """API Source基础Schema"""
    name: str = Field(..., description="显示名称")
    base_url: str = Field(..., description="API基础URL")
    api_key: str = Field(..., description="API密钥")
    enabled: bool = Field(default=True, description="是否启用")
    priority: int = Field(default=0, description="优先级")


class APISourceCreate(APISourceBase):
    """创建API Source的Schema"""
    id: str = Field(..., description="唯一标识符")


class APISourceUpdate(BaseModel):
    """更新API Source的Schema"""
    name: Optional[str] = Field(None, description="显示名称")
    base_url: Optional[str] = Field(None, description="API基础URL")
    api_key: Optional[str] = Field(None, description="API密钥")
    enabled: Optional[bool] = Field(None, description="是否启用")
    priority: Optional[int] = Field(None, description="优先级")


class APISourceResponse(APISourceBase):
    """API Source响应Schema"""
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class APISourceTest(BaseModel):
    """API Source测试结果Schema"""
    success: bool
    response_time: Optional[int] = None
    error: Optional[str] = None
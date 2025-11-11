"""
Model Pydantic Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ModelBase(BaseModel):
    """Model基础Schema"""
    original_name: str = Field(..., description="原始模型名称")
    normalized_name: str = Field(..., description="标准化后的名称")
    display_name: Optional[str] = Field(None, description="用户自定义显示名称")
    provider_id: str = Field(..., description="所属Provider ID")
    enabled: bool = Field(default=True, description="是否启用")


class ModelResponse(ModelBase):
    """Model响应Schema"""
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ModelRename(BaseModel):
    """模型重命名Schema"""
    display_name: str = Field(..., description="新的显示名称")


class ModelBatchRename(BaseModel):
    """批量重命名Schema"""
    renames: List[dict] = Field(..., description="重命名列表")
    
    class Config:
        json_schema_extra = {
            "example": {
                "renames": [
                    {"model_id": "model-001", "display_name": "GPT-4 Turbo"},
                    {"model_id": "model-002", "display_name": "GPT-3.5"}
                ]
            }
        }


class ModelBatchDelete(BaseModel):
    """批量删除Schema"""
    model_ids: List[str] = Field(..., description="要删除的模型ID列表")
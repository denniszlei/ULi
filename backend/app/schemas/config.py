"""
Config Pydantic Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class ConfigGenerate(BaseModel):
    """配置生成请求Schema"""
    force: bool = Field(default=False, description="是否强制重新生成")


class ConfigPreview(BaseModel):
    """配置预览响应Schema"""
    gpt_load_config: str = Field(..., description="gpt-load配置（YAML格式）")
    uni_api_config: str = Field(..., description="uni-api配置（YAML格式）")


class ConfigApply(BaseModel):
    """配置应用响应Schema"""
    success: bool
    gpt_load_reloaded: bool
    uni_api_reloaded: bool
    message: Optional[str] = None


class ConfigValidate(BaseModel):
    """配置验证响应Schema"""
    valid: bool
    errors: list[str] = Field(default_factory=list)


class HealthStatus(BaseModel):
    """健康状态Schema"""
    status: str = Field(..., description="healthy | degraded | unhealthy")
    services: Dict[str, Any] = Field(default_factory=dict)
    providers: Dict[str, int] = Field(default_factory=dict)
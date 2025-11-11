"""
Provider相关数据模型
"""
from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.database import Base


class Provider(Base):
    """Provider数据模型（与APISource相同，保留以兼容架构设计）"""
    
    __tablename__ = "providers"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    base_url = Column(String, nullable=False)
    api_key = Column(String, nullable=False)
    enabled = Column(Boolean, default=True)
    priority = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Provider(id={self.id}, name={self.name}, enabled={self.enabled})>"


class ModelMapping(Base):
    """模型映射数据模型"""
    
    __tablename__ = "model_mappings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    unified_name = Column(String, nullable=False, unique=True)
    load_balance_strategy = Column(String, default="round_robin")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<ModelMapping(unified_name={self.unified_name}, strategy={self.load_balance_strategy})>"


class HealthCheck(Base):
    """健康检查记录数据模型"""
    
    __tablename__ = "health_checks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    provider_id = Column(String, ForeignKey("providers.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String, nullable=False)  # 'healthy', 'unhealthy', 'timeout'
    response_time = Column(Integer, nullable=True)  # 毫秒
    error_message = Column(Text, nullable=True)
    checked_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    def __repr__(self):
        return f"<HealthCheck(provider={self.provider_id}, status={self.status}, time={self.response_time}ms)>"
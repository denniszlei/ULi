"""
API Source数据模型
"""
from sqlalchemy import Column, String, Boolean, Integer, DateTime
from sqlalchemy.sql import func
from app.database import Base


class APISource(Base):
    """API提供商数据模型"""
    
    __tablename__ = "api_sources"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    base_url = Column(String, nullable=False)
    api_key = Column(String, nullable=False)
    enabled = Column(Boolean, default=True)
    priority = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<APISource(id={self.id}, name={self.name}, enabled={self.enabled})>"
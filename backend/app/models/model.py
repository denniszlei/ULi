"""
Model数据模型
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Model(Base):
    """模型数据模型"""
    
    __tablename__ = "models"
    
    id = Column(String, primary_key=True, index=True)
    original_name = Column(String, nullable=False)
    normalized_name = Column(String, nullable=False, index=True)
    display_name = Column(String, nullable=True)
    provider_id = Column(String, ForeignKey("api_sources.id", ondelete="CASCADE"), nullable=False)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Model(id={self.id}, name={self.display_name or self.normalized_name}, provider={self.provider_id})>"
"""
Providers路由
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

router = APIRouter()


@router.get("/providers")
async def get_providers(db: AsyncSession = Depends(get_db)):
    """获取Provider列表"""
    # TODO: 实现查询逻辑
    return {"providers": [], "total": 0}


@router.get("/mappings")
async def get_mappings(db: AsyncSession = Depends(get_db)):
    """获取模型映射列表"""
    # TODO: 实现查询逻辑
    return {"mappings": [], "total": 0}


@router.get("/mappings/groups")
async def get_model_groups(db: AsyncSession = Depends(get_db)):
    """获取模型分组信息"""
    # TODO: 实现查询逻辑
    return {"groups": {}}


@router.get("/mappings/splits")
async def get_provider_splits(db: AsyncSession = Depends(get_db)):
    """获取Provider拆分信息"""
    # TODO: 实现查询逻辑
    return {"splits": []}
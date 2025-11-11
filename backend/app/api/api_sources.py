"""
API Sources路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.api_source import APISourceCreate, APISourceUpdate, APISourceResponse
from app.models.api_source import APISource

router = APIRouter()


@router.get("/api-sources", response_model=List[APISourceResponse])
async def get_api_sources(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """获取API Source列表"""
    # TODO: 实现查询逻辑
    return []


@router.post("/api-sources", response_model=APISourceResponse)
async def create_api_source(
    api_source: APISourceCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建API Source"""
    # TODO: 实现创建逻辑
    raise HTTPException(status_code=501, detail="Not implemented")


@router.put("/api-sources/{source_id}", response_model=APISourceResponse)
async def update_api_source(
    source_id: str,
    api_source: APISourceUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新API Source"""
    # TODO: 实现更新逻辑
    raise HTTPException(status_code=501, detail="Not implemented")


@router.delete("/api-sources/{source_id}")
async def delete_api_source(
    source_id: str,
    db: AsyncSession = Depends(get_db)
):
    """删除API Source"""
    # TODO: 实现删除逻辑
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/api-sources/{source_id}/test")
async def test_api_source(
    source_id: str,
    db: AsyncSession = Depends(get_db)
):
    """测试API Source连接"""
    # TODO: 实现测试逻辑
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/api-sources/{source_id}/refresh")
async def refresh_models(
    source_id: str,
    db: AsyncSession = Depends(get_db)
):
    """刷新API Source的模型列表"""
    # TODO: 实现刷新逻辑
    raise HTTPException(status_code=501, detail="Not implemented")
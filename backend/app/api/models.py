"""
Models路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.model import ModelResponse, ModelRename, ModelBatchRename, ModelBatchDelete

router = APIRouter()


@router.get("/models", response_model=List[ModelResponse])
async def get_models(
    provider_id: str = None,
    enabled: bool = None,
    search: str = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """获取模型列表"""
    # TODO: 实现查询逻辑
    return []


@router.get("/models/{model_id}", response_model=ModelResponse)
async def get_model(
    model_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取单个模型"""
    # TODO: 实现查询逻辑
    raise HTTPException(status_code=404, detail="Model not found")


@router.put("/models/{model_id}/rename", response_model=ModelResponse)
async def rename_model(
    model_id: str,
    rename_data: ModelRename,
    db: AsyncSession = Depends(get_db)
):
    """重命名模型"""
    # TODO: 实现重命名逻辑
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/models/batch-rename")
async def batch_rename_models(
    batch_data: ModelBatchRename,
    db: AsyncSession = Depends(get_db)
):
    """批量重命名模型"""
    # TODO: 实现批量重命名逻辑
    raise HTTPException(status_code=501, detail="Not implemented")


@router.delete("/models/{model_id}")
async def delete_model(
    model_id: str,
    db: AsyncSession = Depends(get_db)
):
    """删除模型（软删除）"""
    # TODO: 实现删除逻辑
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/models/batch-delete")
async def batch_delete_models(
    batch_data: ModelBatchDelete,
    db: AsyncSession = Depends(get_db)
):
    """批量删除模型"""
    # TODO: 实现批量删除逻辑
    raise HTTPException(status_code=501, detail="Not implemented")
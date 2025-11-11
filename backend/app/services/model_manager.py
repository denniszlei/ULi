"""
模型管理服务
负责模型重命名、删除和映射管理
"""
import logging
import uuid
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from collections import defaultdict

from app.models.model import Model
from app.models.api_source import APISource
from app.models.provider_model import Provider, ModelMapping

logger = logging.getLogger(__name__)


class ModelManagerService:
    """模型管理服务"""
    
    def __init__(self, db: AsyncSession):
        """
        初始化模型管理服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
    
    async def create_or_update_model(self, model_data: Dict) -> Model:
        """
        创建或更新模型
        
        Args:
            model_data: 模型数据，包含:
                - original_name: 原始模型名称
                - normalized_name: 标准化名称
                - provider_id: Provider ID
                - display_name: 显示名称（可选）
                
        Returns:
            创建或更新后的模型对象
        """
        try:
            # 检查模型是否已存在
            stmt = select(Model).where(
                and_(
                    Model.original_name == model_data['original_name'],
                    Model.provider_id == model_data['provider_id']
                )
            )
            result = await self.db.execute(stmt)
            existing_model = result.scalar_one_or_none()
            
            if existing_model:
                # 更新现有模型
                existing_model.normalized_name = model_data.get('normalized_name', existing_model.normalized_name)
                if 'display_name' in model_data:
                    existing_model.display_name = model_data['display_name']
                existing_model.updated_at = datetime.utcnow()
                
                logger.info(f"更新模型: {existing_model.id}")
                await self.db.commit()
                await self.db.refresh(existing_model)
                return existing_model
            else:
                # 创建新模型
                model_id = str(uuid.uuid4())
                new_model = Model(
                    id=model_id,
                    original_name=model_data['original_name'],
                    normalized_name=model_data['normalized_name'],
                    display_name=model_data.get('display_name'),
                    provider_id=model_data['provider_id'],
                    enabled=True
                )
                
                self.db.add(new_model)
                await self.db.commit()
                await self.db.refresh(new_model)
                
                logger.info(f"创建新模型: {new_model.id} - {new_model.original_name}")
                return new_model
                
        except Exception as e:
            await self.db.rollback()
            logger.error(f"创建或更新模型失败: {e}")
            raise
    
    async def rename_model(self, model_id: str, new_name: str) -> Optional[Model]:
        """
        重命名模型
        
        Args:
            model_id: 模型ID
            new_name: 新的显示名称
            
        Returns:
            更新后的模型对象，如果模型不存在则返回None
        """
        try:
            # 获取模型
            stmt = select(Model).where(Model.id == model_id)
            result = await self.db.execute(stmt)
            model = result.scalar_one_or_none()
            
            if not model:
                logger.warning(f"模型不存在: {model_id}")
                return None
            
            # 验证新名称的唯一性（在同一provider下）
            check_stmt = select(Model).where(
                and_(
                    Model.display_name == new_name,
                    Model.provider_id == model.provider_id,
                    Model.id != model_id
                )
            )
            check_result = await self.db.execute(check_stmt)
            existing = check_result.scalar_one_or_none()
            
            if existing:
                logger.warning(f"显示名称已存在: {new_name}")
                raise ValueError(f"显示名称 '{new_name}' 已被使用")
            
            # 更新模型名称
            old_name = model.display_name or model.normalized_name
            model.display_name = new_name
            model.updated_at = datetime.utcnow()
            
            await self.db.commit()
            await self.db.refresh(model)
            
            logger.info(f"模型重命名成功: {model_id} - {old_name} -> {new_name}")
            return model
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"重命名模型失败: {e}")
            raise
    
    async def delete_model(self, model_id: str) -> bool:
        """
        删除模型（软删除）
        
        Args:
            model_id: 模型ID
            
        Returns:
            是否删除成功
        """
        try:
            # 获取模型
            stmt = select(Model).where(Model.id == model_id)
            result = await self.db.execute(stmt)
            model = result.scalar_one_or_none()
            
            if not model:
                logger.warning(f"模型不存在: {model_id}")
                return False
            
            # 软删除（标记为禁用）
            model.enabled = False
            model.updated_at = datetime.utcnow()
            
            await self.db.commit()
            
            logger.info(f"模型已删除（软删除）: {model_id} - {model.original_name}")
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"删除模型失败: {e}")
            raise
    
    async def split_providers_by_model(self, api_source_id: str) -> List[Dict]:
        """
        Provider自动拆分
        
        为同一API源的不同模型创建独立的provider实例
        命名规则：{source_name}-{index}
        
        Args:
            api_source_id: API源ID
            
        Returns:
            拆分后的provider列表
        """
        try:
            # 获取API源信息
            api_source_stmt = select(APISource).where(APISource.id == api_source_id)
            api_source_result = await self.db.execute(api_source_stmt)
            api_source = api_source_result.scalar_one_or_none()
            
            if not api_source:
                logger.warning(f"API源不存在: {api_source_id}")
                return []
            
            # 获取该API源的所有启用模型
            models_stmt = select(Model).where(
                and_(
                    Model.provider_id == api_source_id,
                    Model.enabled == True
                )
            )
            models_result = await self.db.execute(models_stmt)
            models = models_result.scalars().all()
            
            if not models:
                logger.info(f"API源 {api_source_id} 没有启用的模型")
                return []
            
            # 按模型名称分组
            models_by_name = defaultdict(list)
            for model in models:
                unified_name = model.display_name or model.normalized_name
                models_by_name[unified_name].append(model)
            
            # 创建拆分的provider
            split_providers = []
            
            for index, model in enumerate(models):
                provider_id = f"{api_source.name}-{index}"
                unified_name = model.display_name or model.normalized_name
                
                # 检查provider是否已存在
                provider_stmt = select(Provider).where(Provider.id == provider_id)
                provider_result = await self.db.execute(provider_stmt)
                existing_provider = provider_result.scalar_one_or_none()
                
                if not existing_provider:
                    # 创建新provider
                    new_provider = Provider(
                        id=provider_id,
                        name=provider_id,
                        base_url=api_source.base_url,
                        api_key=api_source.api_key,
                        enabled=True,
                        priority=api_source.priority
                    )
                    self.db.add(new_provider)
                    
                    split_providers.append({
                        "id": provider_id,
                        "model": unified_name,
                        "original_model": model.original_name,
                        "model_id": model.id
                    })
                    
                    logger.info(f"创建拆分provider: {provider_id} - {unified_name}")
            
            await self.db.commit()
            
            logger.info(f"API源 {api_source_id} 拆分完成，共创建 {len(split_providers)} 个provider")
            return split_providers
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Provider拆分失败: {e}")
            raise
    
    async def get_model_statistics(self) -> Dict:
        """
        获取模型统计信息
        
        Returns:
            统计信息字典
        """
        try:
            # 总模型数
            total_stmt = select(func.count(Model.id))
            total_result = await self.db.execute(total_stmt)
            total_models = total_result.scalar()
            
            # 启用的模型数
            enabled_stmt = select(func.count(Model.id)).where(Model.enabled == True)
            enabled_result = await self.db.execute(enabled_stmt)
            enabled_models = enabled_result.scalar()
            
            # 已删除的模型数
            deleted_models = total_models - enabled_models
            
            # 重命名的模型数
            renamed_stmt = select(func.count(Model.id)).where(Model.display_name.isnot(None))
            renamed_result = await self.db.execute(renamed_stmt)
            renamed_models = renamed_result.scalar()
            
            # 各API源的模型数
            sources_stmt = select(
                APISource.name,
                func.count(Model.id).label('model_count')
            ).join(
                Model, Model.provider_id == APISource.id
            ).where(
                Model.enabled == True
            ).group_by(
                APISource.id, APISource.name
            )
            sources_result = await self.db.execute(sources_stmt)
            sources_stats = [
                {"source_name": row[0], "model_count": row[1]}
                for row in sources_result.all()
            ]
            
            statistics = {
                "total_models": total_models,
                "enabled_models": enabled_models,
                "deleted_models": deleted_models,
                "renamed_models": renamed_models,
                "models_by_source": sources_stats
            }
            
            logger.info(f"模型统计: {statistics}")
            return statistics
            
        except Exception as e:
            logger.error(f"获取模型统计失败: {e}")
            raise
    
    async def batch_rename_models(self, renames: List[Dict]) -> Tuple[List[Model], List[Dict]]:
        """
        批量重命名模型
        
        Args:
            renames: 重命名列表 [{"model_id": str, "new_name": str}, ...]
            
        Returns:
            (成功更新的模型列表, 失败的记录列表)
        """
        updated_models = []
        failed_renames = []
        
        for rename in renames:
            try:
                model_id = rename.get('model_id')
                new_name = rename.get('new_name')
                
                if not model_id or not new_name:
                    failed_renames.append({
                        "model_id": model_id,
                        "error": "缺少必要参数"
                    })
                    continue
                
                model = await self.rename_model(model_id, new_name)
                if model:
                    updated_models.append(model)
                else:
                    failed_renames.append({
                        "model_id": model_id,
                        "error": "模型不存在"
                    })
                    
            except Exception as e:
                failed_renames.append({
                    "model_id": rename.get('model_id'),
                    "error": str(e)
                })
                logger.error(f"批量重命名失败: {rename.get('model_id')} - {e}")
        
        logger.info(f"批量重命名完成: 成功 {len(updated_models)}, 失败 {len(failed_renames)}")
        return updated_models, failed_renames
    
    async def batch_delete_models(self, model_ids: List[str]) -> Tuple[int, List[Dict]]:
        """
        批量删除模型
        
        Args:
            model_ids: 模型ID列表
            
        Returns:
            (成功删除的数量, 失败的记录列表)
        """
        deleted_count = 0
        failed_deletes = []
        
        for model_id in model_ids:
            try:
                success = await self.delete_model(model_id)
                if success:
                    deleted_count += 1
                else:
                    failed_deletes.append({
                        "model_id": model_id,
                        "error": "模型不存在"
                    })
                    
            except Exception as e:
                failed_deletes.append({
                    "model_id": model_id,
                    "error": str(e)
                })
                logger.error(f"批量删除失败: {model_id} - {e}")
        
        logger.info(f"批量删除完成: 成功 {deleted_count}, 失败 {len(failed_deletes)}")
        return deleted_count, failed_deletes
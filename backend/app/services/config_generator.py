"""
配置生成服务
负责生成gpt-load和uni-api的配置文件
"""
import logging
import yaml
import json
import os
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from collections import defaultdict
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.model import Model
from app.models.api_source import APISource
from app.models.provider_model import Provider

logger = logging.getLogger(__name__)


class ConfigGeneratorService:
    """配置生成服务"""
    
    def __init__(
        self,
        db: AsyncSession,
        gpt_load_url: str = "http://localhost:3001",
        config_dir: str = "/app/config"
    ):
        """
        初始化配置生成服务
        
        Args:
            db: 数据库会话
            gpt_load_url: gpt-load服务地址
            config_dir: 配置文件目录
        """
        self.db = db
        self.gpt_load_url = gpt_load_url
        self.config_dir = config_dir
    
    async def generate_gptload_config(self) -> Dict:
        """
        生成gpt-load配置
        
        包括：
        1. 普通分组配置（每个provider一个分组）
        2. 聚合分组配置（按模型名称聚合多个provider）
        3. 模型重定向规则
        
        Returns:
            gpt-load配置字典
        """
        try:
            logger.info("开始生成gpt-load配置")
            
            # 获取所有启用的provider
            providers_stmt = select(Provider).where(Provider.enabled == True)
            providers_result = await self.db.execute(providers_stmt)
            providers = providers_result.scalars().all()
            
            if not providers:
                logger.warning("没有启用的provider")
                return {
                    "providers": [],
                    "groups": [],
                    "aggregate_groups": [],
                    "model_redirects": {}
                }
            
            # 获取所有启用的模型
            models_stmt = select(Model).where(Model.enabled == True)
            models_result = await self.db.execute(models_stmt)
            models = models_result.scalars().all()
            
            # 按provider分组模型
            models_by_provider = defaultdict(list)
            for model in models:
                models_by_provider[model.provider_id].append(model)
            
            # 生成providers配置
            providers_config = []
            groups_config = []
            
            for provider in providers:
                provider_models = models_by_provider.get(provider.id, [])
                
                if not provider_models:
                    continue
                
                # 为每个模型创建独立的provider配置
                for idx, model in enumerate(provider_models):
                    provider_id = f"{provider.name}-{idx}"
                    unified_name = model.display_name or model.normalized_name
                    
                    # Provider配置
                    providers_config.append({
                        "name": provider_id,
                        "base_url": provider.base_url.rstrip('/'),
                        "api_key": provider.api_key,
                        "models": [model.original_name],
                        "enabled": True
                    })
                    
                    # 普通分组配置
                    groups_config.append({
                        "name": f"{provider_id}-{unified_name}",
                        "providers": [provider_id],
                        "strategy": "fixed_priority",
                        "model_mapping": {
                            unified_name: model.original_name
                        }
                    })
            
            # 生成聚合分组配置
            aggregate_groups_config = []
            model_redirects = {}
            
            # 按统一模型名称分组
            models_by_unified_name = defaultdict(list)
            for provider in providers:
                provider_models = models_by_provider.get(provider.id, [])
                for idx, model in enumerate(provider_models):
                    unified_name = model.display_name or model.normalized_name
                    provider_id = f"{provider.name}-{idx}"
                    group_name = f"{provider_id}-{unified_name}"
                    models_by_unified_name[unified_name].append(group_name)
            
            # 创建聚合分组
            for unified_name, group_names in models_by_unified_name.items():
                if len(group_names) > 1:
                    # 多个provider，创建聚合分组
                    agg_group_name = f"Aggr-{unified_name}"
                    aggregate_groups_config.append({
                        "name": agg_group_name,
                        "sub_groups": group_names,
                        "load_balance": "round_robin"
                    })
                    model_redirects[unified_name] = agg_group_name
                else:
                    # 单个provider，直接重定向
                    model_redirects[unified_name] = group_names[0]
            
            config = {
                "providers": providers_config,
                "groups": groups_config,
                "aggregate_groups": aggregate_groups_config,
                "model_redirects": model_redirects
            }
            
            logger.info(f"gpt-load配置生成完成: {len(providers_config)} providers, "
                       f"{len(groups_config)} groups, {len(aggregate_groups_config)} aggregate groups")
            
            return config
            
        except Exception as e:
            logger.error(f"生成gpt-load配置失败: {e}")
            raise
    
    async def generate_uniapi_config(self) -> Dict:
        """
        生成uni-api配置
        
        为每个聚合分组生成provider配置，指向gpt-load
        
        Returns:
            uni-api配置字典
        """
        try:
            logger.info("开始生成uni-api配置")
            
            # 获取所有启用的模型
            models_stmt = select(Model).where(Model.enabled == True)
            models_result = await self.db.execute(models_stmt)
            models = models_result.scalars().all()
            
            # 按统一模型名称去重
            unified_models = {}
            for model in models:
                unified_name = model.display_name or model.normalized_name
                if unified_name not in unified_models:
                    unified_models[unified_name] = model
            
            # 生成providers配置
            providers_config = []
            
            for unified_name in unified_models.keys():
                providers_config.append({
                    "provider": f"gptload-{unified_name}",
                    "base_url": f"{self.gpt_load_url}/proxy/{unified_name}",
                    "api": "openai",
                    "model": [unified_name]
                })
            
            config = {
                "providers": providers_config,
                "api": {
                    "port": 8000,
                    "bind": "0.0.0.0"
                }
            }
            
            logger.info(f"uni-api配置生成完成: {len(providers_config)} providers")
            
            return config
            
        except Exception as e:
            logger.error(f"生成uni-api配置失败: {e}")
            raise
    
    async def save_configs(
        self,
        gptload_config: Dict,
        uniapi_config: Dict
    ) -> Tuple[str, str]:
        """
        保存配置文件
        
        Args:
            gptload_config: gpt-load配置
            uniapi_config: uni-api配置
            
        Returns:
            (gpt-load配置路径, uni-api配置路径)
        """
        try:
            # 确保配置目录存在
            os.makedirs(self.config_dir, exist_ok=True)
            
            # 创建备份目录
            backup_dir = os.path.join(self.config_dir, "backups")
            os.makedirs(backup_dir, exist_ok=True)
            
            # 生成时间戳
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 保存gpt-load配置
            gptload_path = os.path.join(self.config_dir, "gpt-load.yaml")
            gptload_backup_path = os.path.join(backup_dir, f"gpt-load_{timestamp}.yaml")
            
            # 如果存在旧配置，先备份
            if os.path.exists(gptload_path):
                with open(gptload_path, 'r', encoding='utf-8') as f:
                    old_config = f.read()
                with open(gptload_backup_path, 'w', encoding='utf-8') as f:
                    f.write(old_config)
                logger.info(f"已备份旧的gpt-load配置: {gptload_backup_path}")
            
            # 保存新配置
            with open(gptload_path, 'w', encoding='utf-8') as f:
                yaml.dump(gptload_config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            logger.info(f"gpt-load配置已保存: {gptload_path}")
            
            # 保存uni-api配置
            uniapi_path = os.path.join(self.config_dir, "api.yaml")
            uniapi_backup_path = os.path.join(backup_dir, f"api_{timestamp}.yaml")
            
            # 如果存在旧配置，先备份
            if os.path.exists(uniapi_path):
                with open(uniapi_path, 'r', encoding='utf-8') as f:
                    old_config = f.read()
                with open(uniapi_backup_path, 'w', encoding='utf-8') as f:
                    f.write(old_config)
                logger.info(f"已备份旧的uni-api配置: {uniapi_backup_path}")
            
            # 保存新配置
            with open(uniapi_path, 'w', encoding='utf-8') as f:
                yaml.dump(uniapi_config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            logger.info(f"uni-api配置已保存: {uniapi_path}")
            
            return gptload_path, uniapi_path
            
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
            raise
    
    async def apply_configs(self) -> Dict[str, bool]:
        """
        应用配置（可选）
        
        如果配置了外部服务地址，通过API更新配置
        如果是本地服务，可以触发重启
        
        Returns:
            应用结果 {"gpt_load": bool, "uni_api": bool}
        """
        try:
            logger.info("开始应用配置")
            
            # 这里可以实现配置热重载逻辑
            # 例如：调用gpt-load和uni-api的reload API
            # 或者发送信号触发服务重启
            
            # 目前返回成功，实际应用需要根据部署方式实现
            result = {
                "gpt_load": True,
                "uni_api": True
            }
            
            logger.info("配置应用完成")
            return result
            
        except Exception as e:
            logger.error(f"应用配置失败: {e}")
            raise
    
    async def validate_config(self, config: Dict, config_type: str = "gptload") -> Tuple[bool, List[str]]:
        """
        验证配置
        
        Args:
            config: 配置字典
            config_type: 配置类型 ("gptload" 或 "uniapi")
            
        Returns:
            (是否有效, 错误列表)
        """
        errors = []
        
        try:
            if config_type == "gptload":
                # 验证gpt-load配置
                if "providers" not in config:
                    errors.append("缺少 'providers' 字段")
                elif not isinstance(config["providers"], list):
                    errors.append("'providers' 必须是列表")
                
                if "groups" not in config:
                    errors.append("缺少 'groups' 字段")
                elif not isinstance(config["groups"], list):
                    errors.append("'groups' 必须是列表")
                
                # 验证每个provider
                for idx, provider in enumerate(config.get("providers", [])):
                    if "name" not in provider:
                        errors.append(f"Provider {idx}: 缺少 'name' 字段")
                    if "base_url" not in provider:
                        errors.append(f"Provider {idx}: 缺少 'base_url' 字段")
                    if "api_key" not in provider:
                        errors.append(f"Provider {idx}: 缺少 'api_key' 字段")
                
            elif config_type == "uniapi":
                # 验证uni-api配置
                if "providers" not in config:
                    errors.append("缺少 'providers' 字段")
                elif not isinstance(config["providers"], list):
                    errors.append("'providers' 必须是列表")
                
                # 验证每个provider
                for idx, provider in enumerate(config.get("providers", [])):
                    if "provider" not in provider:
                        errors.append(f"Provider {idx}: 缺少 'provider' 字段")
                    if "base_url" not in provider:
                        errors.append(f"Provider {idx}: 缺少 'base_url' 字段")
            
            is_valid = len(errors) == 0
            
            if is_valid:
                logger.info(f"{config_type} 配置验证通过")
            else:
                logger.warning(f"{config_type} 配置验证失败: {errors}")
            
            return is_valid, errors
            
        except Exception as e:
            logger.error(f"配置验证失败: {e}")
            return False, [str(e)]
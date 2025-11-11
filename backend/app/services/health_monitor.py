"""
健康监控服务
负责定期检测API提供商的可用性
"""
import logging
import time
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc

from app.models.api_source import APISource
from app.models.provider_model import Provider, HealthCheck

logger = logging.getLogger(__name__)


class HealthMonitorService:
    """健康监控服务"""
    
    def __init__(self, db: AsyncSession, timeout: int = 30, max_concurrent: int = 10):
        """
        初始化健康监控服务
        
        Args:
            db: 数据库会话
            timeout: 请求超时时间（秒）
            max_concurrent: 最大并发检查数
        """
        self.db = db
        self.client = httpx.AsyncClient(timeout=timeout)
        self.timeout = timeout
        self.max_concurrent = max_concurrent
    
    async def check_api_source_health(self, api_source_id: str) -> Dict:
        """
        检查API源健康状态
        
        Args:
            api_source_id: API源ID
            
        Returns:
            健康检查结果
        """
        try:
            # 获取API源信息
            stmt = select(APISource).where(APISource.id == api_source_id)
            result = await self.db.execute(stmt)
            api_source = result.scalar_one_or_none()
            
            if not api_source:
                logger.warning(f"API源不存在: {api_source_id}")
                return {
                    "api_source_id": api_source_id,
                    "status": "not_found",
                    "response_time": None,
                    "error": "API源不存在"
                }
            
            # 执行健康检查
            url = api_source.base_url.rstrip('/')
            if not url.endswith('/v1'):
                url = f"{url}/v1"
            
            start_time = time.time()
            
            try:
                response = await self.client.get(
                    f"{url}/models",
                    headers={"Authorization": f"Bearer {api_source.api_key}"},
                    timeout=self.timeout
                )
                
                response_time = int((time.time() - start_time) * 1000)
                
                if response.status_code == 200:
                    status = "healthy"
                    error = None
                    logger.info(f"API源 {api_source_id} 健康检查通过，响应时间: {response_time}ms")
                else:
                    status = "unhealthy"
                    error = f"HTTP {response.status_code}"
                    logger.warning(f"API源 {api_source_id} 健康检查失败: {error}")
                
            except httpx.TimeoutException:
                response_time = int((time.time() - start_time) * 1000)
                status = "timeout"
                error = "请求超时"
                logger.error(f"API源 {api_source_id} 健康检查超时")
                
            except Exception as e:
                response_time = int((time.time() - start_time) * 1000)
                status = "unhealthy"
                error = str(e)
                logger.error(f"API源 {api_source_id} 健康检查异常: {error}")
            
            # 保存健康检查记录
            health_check = HealthCheck(
                provider_id=api_source_id,
                status=status,
                response_time=response_time if status != "timeout" else None,
                error_message=error
            )
            self.db.add(health_check)
            await self.db.commit()
            
            return {
                "api_source_id": api_source_id,
                "status": status,
                "response_time": response_time,
                "error": error,
                "checked_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"检查API源健康状态失败: {e}")
            return {
                "api_source_id": api_source_id,
                "status": "error",
                "response_time": None,
                "error": str(e)
            }
    
    async def check_all_sources(self) -> Dict:
        """
        检查所有API源
        
        Returns:
            {
                "results": List[Dict],  # 每个源的检查结果
                "summary": {
                    "total": int,
                    "healthy": int,
                    "unhealthy": int,
                    "timeout": int
                }
            }
        """
        try:
            logger.info("开始检查所有API源的健康状态")
            
            # 获取所有启用的API源
            stmt = select(APISource).where(APISource.enabled == True)
            result = await self.db.execute(stmt)
            api_sources = result.scalars().all()
            
            if not api_sources:
                logger.warning("没有启用的API源")
                return {
                    "results": [],
                    "summary": {
                        "total": 0,
                        "healthy": 0,
                        "unhealthy": 0,
                        "timeout": 0
                    }
                }
            
            # 使用信号量限制并发
            semaphore = asyncio.Semaphore(self.max_concurrent)
            
            async def check_with_semaphore(source):
                async with semaphore:
                    return await self.check_api_source_health(source.id)
            
            # 并发执行健康检查
            tasks = [check_with_semaphore(source) for source in api_sources]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理结果
            valid_results = []
            for result in results:
                if isinstance(result, dict):
                    valid_results.append(result)
                else:
                    logger.error(f"健康检查异常: {result}")
            
            # 统计结果
            summary = {
                "total": len(valid_results),
                "healthy": sum(1 for r in valid_results if r["status"] == "healthy"),
                "unhealthy": sum(1 for r in valid_results if r["status"] == "unhealthy"),
                "timeout": sum(1 for r in valid_results if r["status"] == "timeout")
            }
            
            logger.info(f"健康检查完成: {summary}")
            
            return {
                "results": valid_results,
                "summary": summary
            }
            
        except Exception as e:
            logger.error(f"批量健康检查失败: {e}")
            raise
    
    async def get_health_statistics(self) -> Dict:
        """
        获取健康统计
        
        Returns:
            统计信息字典
        """
        try:
            # 获取所有API源数量
            total_stmt = select(func.count(APISource.id))
            total_result = await self.db.execute(total_stmt)
            total_sources = total_result.scalar()
            
            # 获取启用的API源数量
            enabled_stmt = select(func.count(APISource.id)).where(APISource.enabled == True)
            enabled_result = await self.db.execute(enabled_stmt)
            enabled_sources = enabled_result.scalar()
            
            # 获取最近的健康检查记录
            # 为每个provider获取最新的健康检查记录
            subquery = (
                select(
                    HealthCheck.provider_id,
                    func.max(HealthCheck.checked_at).label('latest_check')
                )
                .group_by(HealthCheck.provider_id)
                .subquery()
            )
            
            latest_checks_stmt = (
                select(HealthCheck)
                .join(
                    subquery,
                    and_(
                        HealthCheck.provider_id == subquery.c.provider_id,
                        HealthCheck.checked_at == subquery.c.latest_check
                    )
                )
            )
            latest_checks_result = await self.db.execute(latest_checks_stmt)
            latest_checks = latest_checks_result.scalars().all()
            
            # 统计健康状态
            healthy_count = sum(1 for check in latest_checks if check.status == "healthy")
            unhealthy_count = sum(1 for check in latest_checks if check.status in ["unhealthy", "timeout"])
            
            # 计算平均响应时间
            response_times = [check.response_time for check in latest_checks if check.response_time is not None]
            avg_response_time = int(sum(response_times) / len(response_times)) if response_times else 0
            
            # 获取故障源列表
            failed_sources = [
                {
                    "provider_id": check.provider_id,
                    "status": check.status,
                    "error": check.error_message,
                    "checked_at": check.checked_at.isoformat() if check.checked_at else None
                }
                for check in latest_checks
                if check.status in ["unhealthy", "timeout"]
            ]
            
            # 获取最近检查时间
            if latest_checks:
                last_check_time = max(check.checked_at for check in latest_checks if check.checked_at)
                last_check_time_str = last_check_time.isoformat() if last_check_time else None
            else:
                last_check_time_str = None
            
            statistics = {
                "total_sources": total_sources,
                "enabled_sources": enabled_sources,
                "online_sources": healthy_count,
                "offline_sources": unhealthy_count,
                "avg_response_time": avg_response_time,
                "last_check_time": last_check_time_str,
                "failed_sources": failed_sources
            }
            
            logger.info(f"健康统计: 在线 {healthy_count}/{enabled_sources}, 平均响应时间 {avg_response_time}ms")
            
            return statistics
            
        except Exception as e:
            logger.error(f"获取健康统计失败: {e}")
            raise
    
    async def get_provider_health_history(
        self,
        provider_id: str,
        limit: int = 100
    ) -> List[Dict]:
        """
        获取Provider的健康检查历史
        
        Args:
            provider_id: Provider ID
            limit: 返回记录数量限制
            
        Returns:
            健康检查历史记录列表
        """
        try:
            stmt = (
                select(HealthCheck)
                .where(HealthCheck.provider_id == provider_id)
                .order_by(desc(HealthCheck.checked_at))
                .limit(limit)
            )
            result = await self.db.execute(stmt)
            checks = result.scalars().all()
            
            history = [
                {
                    "status": check.status,
                    "response_time": check.response_time,
                    "error": check.error_message,
                    "checked_at": check.checked_at.isoformat() if check.checked_at else None
                }
                for check in checks
            ]
            
            return history
            
        except Exception as e:
            logger.error(f"获取健康检查历史失败: {e}")
            raise
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()
        logger.info("健康监控服务已关闭")
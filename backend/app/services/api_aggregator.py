"""
API聚合服务
负责从多个API提供商获取模型列表
"""
import logging
import re
import asyncio
from typing import List, Dict, Optional, Tuple
import httpx

logger = logging.getLogger(__name__)


class APIAggregatorService:
    """API聚合服务"""
    
    def __init__(self, max_concurrent: int = 5):
        """
        初始化API聚合服务
        
        Args:
            max_concurrent: 最大并发请求数
        """
        self.client = httpx.AsyncClient(timeout=30.0)
        self.max_concurrent = max_concurrent
        self.max_retries = 3
        self.backoff_factor = 2
    
    async def fetch_models(
        self,
        base_url: str,
        api_key: str,
        retry_count: int = 0
    ) -> Tuple[bool, Optional[List[Dict]], Optional[str]]:
        """
        从API源获取模型列表
        
        Args:
            base_url: API基础URL
            api_key: API密钥
            retry_count: 当前重试次数
            
        Returns:
            (成功标志, 模型列表, 错误信息)
        """
        # 确保URL格式正确
        url = base_url.rstrip('/')
        if not url.endswith('/v1'):
            url = f"{url}/v1"
        
        try:
            logger.info(f"正在获取模型列表: {url}/models")
            
            response = await self.client.get(
                f"{url}/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=30.0
            )
            
            # 检查响应状态
            if response.status_code == 429:  # 速率限制
                if retry_count < self.max_retries:
                    wait_time = self.backoff_factor ** retry_count
                    logger.warning(f"遇到速率限制，等待 {wait_time} 秒后重试...")
                    await asyncio.sleep(wait_time)
                    return await self.fetch_models(base_url, api_key, retry_count + 1)
                else:
                    return False, None, "超过最大重试次数（速率限制）"
            
            response.raise_for_status()
            data = response.json()
            
            # 处理不同的响应格式
            models = []
            if isinstance(data, dict):
                # OpenAI格式: {"data": [...], "object": "list"}
                if "data" in data:
                    models = data["data"]
                # 自定义格式: {"models": [...]}
                elif "models" in data:
                    models = data["models"]
                # 直接是模型列表
                elif "object" in data and data.get("object") == "list":
                    models = data.get("data", [])
            elif isinstance(data, list):
                # 直接返回列表
                models = data
            
            logger.info(f"成功获取 {len(models)} 个模型")
            return True, models, None
            
        except httpx.TimeoutException:
            error_msg = "请求超时"
            logger.error(f"获取模型列表超时: {url}")
            
            if retry_count < self.max_retries:
                wait_time = self.backoff_factor ** retry_count
                logger.info(f"等待 {wait_time} 秒后重试...")
                await asyncio.sleep(wait_time)
                return await self.fetch_models(base_url, api_key, retry_count + 1)
            
            return False, None, error_msg
            
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP错误: {e.response.status_code}"
            logger.error(f"获取模型列表失败: {error_msg}")
            
            # 对于5xx错误进行重试
            if 500 <= e.response.status_code < 600 and retry_count < self.max_retries:
                wait_time = self.backoff_factor ** retry_count
                logger.info(f"服务器错误，等待 {wait_time} 秒后重试...")
                await asyncio.sleep(wait_time)
                return await self.fetch_models(base_url, api_key, retry_count + 1)
            
            return False, None, error_msg
            
        except Exception as e:
            error_msg = f"未知错误: {str(e)}"
            logger.error(f"获取模型列表失败: {error_msg}")
            return False, None, error_msg
    
    def normalize_model_name(self, model_name: str) -> str:
        """
        标准化模型名称
        
        规则：
        1. 移除provider前缀（如 openai/, anthropic/）
        2. 移除版本后缀中的日期（如 -20240620）
        3. 移除preview后缀
        4. 统一转小写
        5. 移除多余空格和特殊字符
        
        Args:
            model_name: 原始模型名称
            
        Returns:
            标准化后的名称
        """
        if not model_name:
            return ""
        
        normalized = model_name.strip()
        
        # 移除provider前缀
        if '/' in normalized:
            parts = normalized.split('/')
            normalized = parts[-1]  # 取最后一部分
        
        # 移除日期后缀 (如 -20240620, -2024-06-20)
        normalized = re.sub(r'-\d{8}$', '', normalized)
        normalized = re.sub(r'-\d{4}-\d{2}-\d{2}$', '', normalized)
        
        # 移除preview后缀
        normalized = re.sub(r'-preview$', '', normalized, flags=re.IGNORECASE)
        
        # 移除其他常见后缀
        normalized = re.sub(r'-latest$', '', normalized, flags=re.IGNORECASE)
        normalized = re.sub(r'-\d{4}$', '', normalized)  # 移除年份后缀
        
        # 转小写
        normalized = normalized.lower()
        
        # 移除多余的连字符
        normalized = re.sub(r'-+', '-', normalized)
        normalized = normalized.strip('-')
        
        # 移除多余空格
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    async def batch_fetch_models(
        self,
        api_sources: List[Dict]
    ) -> Dict[str, Dict]:
        """
        批量获取多个API源的模型
        
        Args:
            api_sources: API源列表，每个元素包含 {id, base_url, api_key}
            
        Returns:
            {
                "results": {
                    "api_source_id": {
                        "success": bool,
                        "models": List[Dict],
                        "error": str
                    }
                },
                "summary": {
                    "total": int,
                    "success": int,
                    "failed": int
                }
            }
        """
        results = {}
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def fetch_with_semaphore(source: Dict):
            """使用信号量限制并发"""
            async with semaphore:
                source_id = source.get('id')
                base_url = source.get('base_url')
                api_key = source.get('api_key')
                
                logger.info(f"开始获取API源 {source_id} 的模型列表")
                
                success, models, error = await self.fetch_models(base_url, api_key)
                
                results[source_id] = {
                    "success": success,
                    "models": models if success else [],
                    "error": error,
                    "model_count": len(models) if models else 0
                }
                
                if success:
                    logger.info(f"API源 {source_id} 获取成功，共 {len(models)} 个模型")
                else:
                    logger.error(f"API源 {source_id} 获取失败: {error}")
        
        # 创建并发任务
        tasks = [fetch_with_semaphore(source) for source in api_sources]
        
        # 等待所有任务完成
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # 统计结果
        success_count = sum(1 for r in results.values() if r["success"])
        failed_count = len(results) - success_count
        
        summary = {
            "total": len(api_sources),
            "success": success_count,
            "failed": failed_count
        }
        
        logger.info(f"批量获取完成: 总计 {summary['total']}, 成功 {summary['success']}, 失败 {summary['failed']}")
        
        return {
            "results": results,
            "summary": summary
        }
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()
        logger.info("API聚合服务已关闭")
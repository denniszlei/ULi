"""
数据库初始化脚本
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.database import engine, Base, init_db
from app.models import api_source, model, provider_model
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """初始化数据库"""
    try:
        logger.info("开始初始化数据库...")
        
        # 创建所有表
        await init_db()
        
        logger.info("数据库初始化完成！")
        logger.info("已创建以下表:")
        logger.info("  - api_sources (API源)")
        logger.info("  - models (模型)")
        logger.info("  - providers (Provider)")
        logger.info("  - model_mappings (模型映射)")
        logger.info("  - health_checks (健康检查记录)")
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
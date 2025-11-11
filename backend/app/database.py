"""
数据库连接和会话管理
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import StaticPool
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# 创建Base类
Base = declarative_base()

# 创建异步引擎
# 对于SQLite，需要使用aiosqlite驱动
database_url = settings.DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")

engine = create_async_engine(
    database_url,
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False} if "sqlite" in database_url else {},
    poolclass=StaticPool if "sqlite" in database_url else None,
)

# 创建会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncSession:
    """
    获取数据库会话
    
    用于FastAPI依赖注入
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    初始化数据库
    
    创建所有表
    """
    try:
        # 导入所有模型以确保它们被注册
        from app.models import api_source, model, provider_model
        
        async with engine.begin() as conn:
            # 创建所有表
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("数据库初始化成功")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise


async def close_db():
    """
    关闭数据库连接
    """
    await engine.dispose()
    logger.info("数据库连接已关闭")
"""
FastAPI应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import init_db
from app.api import api_sources, models, providers, config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    logger.info("初始化数据库...")
    await init_db()
    logger.info("应用启动完成")
    
    yield
    
    # 关闭时清理资源
    logger.info("应用关闭")


# 创建FastAPI应用
app = FastAPI(
    title="uni-load-improved",
    description="LLM大模型API网关整合系统",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(api_sources.router, prefix="/api/v1", tags=["API Sources"])
app.include_router(models.router, prefix="/api/v1", tags=["Models"])
app.include_router(providers.router, prefix="/api/v1", tags=["Providers"])
app.include_router(config.router, prefix="/api/v1", tags=["Config"])

# 挂载静态文件（前端构建产物）
try:
    app.mount("/", StaticFiles(directory="static", html=True), name="static")
except RuntimeError:
    logger.warning("静态文件目录不存在，跳过挂载")


@app.get("/api/v1/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "uni-load-improved"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
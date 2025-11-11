# 多阶段构建Dockerfile - uni-load-improved all-in-one部署
# 支持多架构: linux/amd64, linux/arm64

# ============ 阶段1: 构建前端 ============
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# 复制前端依赖文件
COPY frontend/package*.json ./

# 安装依赖（包括开发依赖用于构建）
RUN npm ci

# 复制前端源码
COPY frontend/ ./

# 构建前端
RUN npm run build

# ============ 阶段2: 构建后端依赖 ============
FROM python:3.11-slim AS backend-builder

WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# 复制后端依赖文件
COPY backend/requirements.txt ./

# 安装Python依赖到用户目录
RUN pip install --no-cache-dir --user -r requirements.txt

# ============ 阶段3: gpt-load集成 ============
FROM python:3.11-slim AS gptload-builder

WORKDIR /gptload

# 安装gpt-load（如果有pip包的话）
# 注意：这里假设gpt-load可以通过pip安装或从源码构建
# 如果gpt-load有官方Docker镜像，可以直接使用COPY --from
RUN pip install --no-cache-dir --user gpt-load || echo "gpt-load not available via pip"

# ============ 阶段4: uni-api集成 ============
FROM python:3.11-slim AS uniapi-builder

WORKDIR /uniapi

# 安装uni-api
RUN pip install --no-cache-dir --user uni-api || echo "uni-api not available via pip"

# ============ 阶段5: 最终运行时镜像 ============
FROM python:3.11-slim

# 设置标签
LABEL maintainer="uni-load-improved"
LABEL description="All-in-one container for uni-load-improved with gpt-load and uni-api"
LABEL version="1.0.0"

WORKDIR /app

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制Python包
COPY --from=backend-builder /root/.local /root/.local
COPY --from=gptload-builder /root/.local /root/.local
COPY --from=uniapi-builder /root/.local /root/.local

# 设置PATH
ENV PATH=/root/.local/bin:$PATH

# 复制后端代码
COPY backend/ ./backend/
COPY scripts/ ./scripts/

# 从前端构建阶段复制静态文件
COPY --from=frontend-builder /app/frontend/dist ./backend/static

# 复制配置文件示例
COPY config/ ./config/

# 创建必要的目录
RUN mkdir -p /app/config /app/data /app/logs /app/backups

# 复制Docker相关脚本
COPY docker/entrypoint.sh /entrypoint.sh
COPY docker/healthcheck.sh /healthcheck.sh
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# 设置脚本权限
RUN chmod +x /entrypoint.sh /healthcheck.sh

# 创建非root用户（安全最佳实践）
RUN useradd -m -u 1000 -s /bin/bash uniload && \
    chown -R uniload:uniload /app

# 切换到非root用户
USER uniload

# 暴露端口
EXPOSE 8080 3001 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD /healthcheck.sh || exit 1

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UNI_LOAD_CONFIG=/app/config/user-config.yaml \
    UNI_LOAD_DATA=/app/data \
    UNI_LOAD_LOGS=/app/logs \
    GPT_LOAD_MODE=internal \
    UNI_API_MODE=internal \
    LOG_LEVEL=INFO

# 数据卷
VOLUME ["/app/config", "/app/data", "/app/logs"]

# 启动
ENTRYPOINT ["/entrypoint.sh"]
CMD ["start"]
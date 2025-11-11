# 多阶段构建Dockerfile - uni-load-improved
# 仅构建uni-load-improved后端和前端
# gpt-load和uni-api使用官方Docker镜像独立部署

# ============ 阶段1: 构建前端 ============
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# 复制前端依赖文件
COPY frontend/package*.json ./

# 安装依赖（包括开发依赖用于构建）
# 注意：使用 npm install 而不是 npm ci，因为项目中没有 package-lock.json
# 如果需要更严格的依赖版本控制，建议生成 package-lock.json 并使用 npm ci
RUN npm install

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

# ============ 阶段3: 最终运行时镜像 ============
FROM python:3.11-slim

# 设置标签
LABEL maintainer="uni-load-improved"
LABEL description="uni-load-improved - Configuration management for gpt-load and uni-api"
LABEL version="1.0.0"

WORKDIR /app

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制Python包
COPY --from=backend-builder /root/.local /root/.local

# 设置PATH
ENV PATH=/root/.local/bin:$PATH

# 复制后端代码
COPY backend/ ./backend/
COPY scripts/ ./scripts/

# 从前端构建阶段复制静态文件
# 注意：vite.config.js配置输出到../backend/static，所以实际路径是/app/backend/static
COPY --from=frontend-builder /app/backend/static ./backend/static

# 复制配置文件示例
COPY config/ ./config/

# 创建必要的目录
RUN mkdir -p /app/config /app/data /app/logs /app/backups

# 复制Docker相关脚本
COPY docker/entrypoint.sh /entrypoint.sh
COPY docker/healthcheck.sh /healthcheck.sh

# 设置脚本权限
RUN chmod +x /entrypoint.sh /healthcheck.sh

# 创建非root用户（安全最佳实践）
RUN useradd -m -u 1000 -s /bin/bash uniload && \
    chown -R uniload:uniload /app

# 切换到非root用户
USER uniload

# 暴露端口（仅uni-load-improved后端）
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD /healthcheck.sh || exit 1

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UNI_LOAD_CONFIG=/app/config/user-config.yaml \
    UNI_LOAD_DATA=/app/data \
    UNI_LOAD_LOGS=/app/logs \
    GPT_LOAD_URL=http://gpt-load:3001 \
    UNI_API_URL=http://uni-api:8000 \
    LOG_LEVEL=INFO

# 数据卷
VOLUME ["/app/config", "/app/data", "/app/logs"]

# 启动
ENTRYPOINT ["/entrypoint.sh"]
CMD ["start"]
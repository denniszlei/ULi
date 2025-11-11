#!/bin/bash
set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 打印启动信息
echo "=========================================="
echo "  uni-load-improved Container Starting"
echo "=========================================="
log_info "Version: 1.0.0"
log_info "Mode: ${GPT_LOAD_MODE:-internal} (gpt-load) | ${UNI_API_MODE:-internal} (uni-api)"
echo ""

# 检查并创建必要的目录
log_info "Checking directories..."
mkdir -p /app/config /app/data /app/logs /app/backups

# 检查配置文件
if [ ! -f "/app/config/user-config.yaml" ]; then
    log_warn "user-config.yaml not found, creating from example..."
    if [ -f "/app/config/config.example.yaml" ]; then
        cp /app/config/config.example.yaml /app/config/user-config.yaml
    else
        log_warn "No example config found, will use defaults"
    fi
fi

# 初始化数据库
if [ ! -f "/app/data/uni-load.db" ]; then
    log_info "Initializing database..."
    cd /app
    python scripts/init_db.py
    if [ $? -eq 0 ]; then
        log_info "Database initialized successfully"
    else
        log_error "Failed to initialize database"
        exit 1
    fi
else
    log_info "Database already exists"
fi

# 运行数据库迁移
log_info "Running database migrations..."
cd /app
python scripts/migrate.py || log_warn "Migration failed or not needed"

# 根据命令参数决定启动方式
case "${1:-start}" in
    start)
        log_info "Starting all services with supervisord..."
        exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
        ;;
    
    backend-only)
        log_info "Starting backend service only..."
        cd /app/backend
        exec uvicorn app.main:app --host 0.0.0.0 --port 8080 --workers ${WORKERS:-4}
        ;;
    
    shell)
        log_info "Starting interactive shell..."
        exec /bin/bash
        ;;
    
    init-db)
        log_info "Initializing database only..."
        cd /app
        python scripts/init_db.py
        ;;
    
    *)
        log_info "Running custom command: $@"
        exec "$@"
        ;;
esac
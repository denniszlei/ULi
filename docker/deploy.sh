#!/bin/bash
# Docker部署脚本
# 支持不同环境的部署和配置验证

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 默认配置
ENVIRONMENT="production"
ACTION="deploy"
COMPOSE_FILE="docker-compose.yml"
PROJECT_NAME="uni-load-improved"

# 打印帮助信息
print_help() {
    cat << EOF
用法: $0 [选项] [动作]

动作:
    deploy      部署服务 (默认)
    start       启动服务
    stop        停止服务
    restart     重启服务
    status      查看服务状态
    logs        查看日志
    backup      备份数据
    restore     恢复数据

选项:
    -e, --env ENV           环境: dev, staging, production (默认: production)
    -f, --file FILE         docker-compose文件 (默认: docker-compose.yml)
    -p, --project NAME      项目名称 (默认: uni-load-improved)
    -h, --help              显示帮助信息

示例:
    # 部署生产环境
    $0 deploy

    # 启动开发环境
    $0 -e dev start

    # 查看日志
    $0 logs

    # 备份数据
    $0 backup
EOF
}

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "docker-compose未安装"
        exit 1
    fi
    
    log_info "依赖检查通过"
}

# 验证配置
validate_config() {
    log_info "验证配置..."
    
    # 检查.env文件
    if [ ! -f ".env" ]; then
        log_warn ".env文件不存在，将从示例创建"
        if [ -f ".env.docker.example" ]; then
            cp .env.docker.example .env
            log_info "已创建.env文件，请检查并修改配置"
        else
            log_error ".env.docker.example文件不存在"
            exit 1
        fi
    fi
    
    # 检查必要的目录
    mkdir -p data/config data/db data/logs data/backups
    
    log_info "配置验证通过"
}

# 部署服务
deploy_service() {
    log_info "部署服务 (环境: ${ENVIRONMENT})..."
    
    check_dependencies
    validate_config
    
    # 拉取最新镜像
    log_info "拉取最新镜像..."
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" pull
    
    # 启动服务
    log_info "启动服务..."
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" up -d
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 10
    
    # 检查服务状态
    check_status
    
    log_info "部署完成!"
}

# 启动服务
start_service() {
    log_info "启动服务..."
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" start
    log_info "服务已启动"
}

# 停止服务
stop_service() {
    log_info "停止服务..."
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" stop
    log_info "服务已停止"
}

# 重启服务
restart_service() {
    log_info "重启服务..."
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" restart
    log_info "服务已重启"
}

# 查看状态
check_status() {
    log_info "服务状态:"
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" ps
    
    # 检查健康状态
    log_info "健康检查:"
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" exec -T uni-load-improved /healthcheck.sh || log_warn "健康检查失败"
}

# 查看日志
view_logs() {
    log_info "查看日志 (Ctrl+C退出)..."
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" logs -f
}

# 备份数据
backup_data() {
    BACKUP_DIR="data/backups/backup-$(date +%Y%m%d-%H%M%S)"
    log_info "备份数据到 ${BACKUP_DIR}..."
    
    mkdir -p "$BACKUP_DIR"
    
    # 备份数据库
    if [ -f "data/db/uni-load.db" ]; then
        cp data/db/uni-load.db "$BACKUP_DIR/"
        log_info "数据库已备份"
    fi
    
    # 备份配置
    if [ -d "data/config" ]; then
        cp -r data/config "$BACKUP_DIR/"
        log_info "配置已备份"
    fi
    
    # 创建压缩包
    tar -czf "${BACKUP_DIR}.tar.gz" -C "$(dirname "$BACKUP_DIR")" "$(basename "$BACKUP_DIR")"
    rm -rf "$BACKUP_DIR"
    
    log_info "备份完成: ${BACKUP_DIR}.tar.gz"
}

# 恢复数据
restore_data() {
    log_info "可用的备份:"
    ls -lh data/backups/*.tar.gz 2>/dev/null || log_warn "没有找到备份文件"
    
    echo ""
    read -p "请输入要恢复的备份文件名: " BACKUP_FILE
    
    if [ ! -f "$BACKUP_FILE" ]; then
        log_error "备份文件不存在: $BACKUP_FILE"
        exit 1
    fi
    
    log_warn "恢复数据将覆盖现有数据，是否继续? (yes/no)"
    read -p "> " CONFIRM
    
    if [ "$CONFIRM" != "yes" ]; then
        log_info "取消恢复"
        exit 0
    fi
    
    # 停止服务
    stop_service
    
    # 解压备份
    TEMP_DIR=$(mktemp -d)
    tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR"
    
    # 恢复数据
    cp -r "$TEMP_DIR"/*/* data/
    rm -rf "$TEMP_DIR"
    
    # 启动服务
    start_service
    
    log_info "数据恢复完成"
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -f|--file)
            COMPOSE_FILE="$2"
            shift 2
            ;;
        -p|--project)
            PROJECT_NAME="$2"
            shift 2
            ;;
        -h|--help)
            print_help
            exit 0
            ;;
        deploy|start|stop|restart|status|logs|backup|restore)
            ACTION="$1"
            shift
            ;;
        *)
            log_error "未知选项: $1"
            print_help
            exit 1
            ;;
    esac
done

# 切换到docker目录
cd "$(dirname "$0")"

# 打印信息
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  uni-load-improved 部署脚本${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}环境:${NC} ${ENVIRONMENT}"
echo -e "${GREEN}动作:${NC} ${ACTION}"
echo -e "${GREEN}项目:${NC} ${PROJECT_NAME}"
echo ""

# 执行动作
case $ACTION in
    deploy)
        deploy_service
        ;;
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
        ;;
    status)
        check_status
        ;;
    logs)
        view_logs
        ;;
    backup)
        backup_data
        ;;
    restore)
        restore_data
        ;;
    *)
        log_error "未知动作: $ACTION"
        print_help
        exit 1
        ;;
esac
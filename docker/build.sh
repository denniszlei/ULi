#!/bin/bash
# Docker镜像构建脚本
# 支持多架构构建和版本标签管理

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 默认配置
IMAGE_NAME="uni-load-improved"
REGISTRY=""
VERSION="latest"
PLATFORMS="linux/amd64,linux/arm64"
BUILD_TYPE="all"  # all, backend, frontend
PUSH=false
NO_CACHE=false

# 打印帮助信息
print_help() {
    cat << EOF
用法: $0 [选项]

选项:
    -n, --name NAME         镜像名称 (默认: uni-load-improved)
    -r, --registry REGISTRY 镜像仓库地址 (例如: docker.io/username)
    -v, --version VERSION   版本标签 (默认: latest)
    -p, --platforms PLATFORMS 目标平台 (默认: linux/amd64,linux/arm64)
    -t, --type TYPE         构建类型: all, backend, frontend (默认: all)
    --push                  构建后推送到仓库
    --no-cache              不使用缓存构建
    -h, --help              显示帮助信息

示例:
    # 构建all-in-one镜像
    $0 -v 1.0.0

    # 构建并推送到Docker Hub
    $0 -r docker.io/username -v 1.0.0 --push

    # 仅构建后端镜像
    $0 -t backend -v 1.0.0

    # 多架构构建
    $0 -p linux/amd64,linux/arm64,linux/arm/v7 -v 1.0.0
EOF
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--name)
            IMAGE_NAME="$2"
            shift 2
            ;;
        -r|--registry)
            REGISTRY="$2"
            shift 2
            ;;
        -v|--version)
            VERSION="$2"
            shift 2
            ;;
        -p|--platforms)
            PLATFORMS="$2"
            shift 2
            ;;
        -t|--type)
            BUILD_TYPE="$2"
            shift 2
            ;;
        --push)
            PUSH=true
            shift
            ;;
        --no-cache)
            NO_CACHE=true
            shift
            ;;
        -h|--help)
            print_help
            exit 0
            ;;
        *)
            echo -e "${RED}错误: 未知选项 $1${NC}"
            print_help
            exit 1
            ;;
    esac
done

# 构建完整镜像名称
if [ -n "$REGISTRY" ]; then
    FULL_IMAGE_NAME="${REGISTRY}/${IMAGE_NAME}"
else
    FULL_IMAGE_NAME="${IMAGE_NAME}"
fi

# 打印构建信息
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Docker镜像构建${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}镜像名称:${NC} ${FULL_IMAGE_NAME}"
echo -e "${GREEN}版本标签:${NC} ${VERSION}"
echo -e "${GREEN}构建类型:${NC} ${BUILD_TYPE}"
echo -e "${GREEN}目标平台:${NC} ${PLATFORMS}"
echo -e "${GREEN}推送镜像:${NC} ${PUSH}"
echo -e "${GREEN}使用缓存:${NC} $( [ "$NO_CACHE" = true ] && echo "否" || echo "是" )"
echo ""

# 切换到项目根目录
cd "$(dirname "$0")/.."

# 检查Docker buildx
if ! docker buildx version > /dev/null 2>&1; then
    echo -e "${RED}错误: Docker buildx未安装或未启用${NC}"
    exit 1
fi

# 创建或使用buildx builder
BUILDER_NAME="multiarch-builder"
if ! docker buildx inspect "$BUILDER_NAME" > /dev/null 2>&1; then
    echo -e "${YELLOW}创建buildx builder: ${BUILDER_NAME}${NC}"
    docker buildx create --name "$BUILDER_NAME" --use
else
    echo -e "${GREEN}使用现有buildx builder: ${BUILDER_NAME}${NC}"
    docker buildx use "$BUILDER_NAME"
fi

# 构建参数
BUILD_ARGS=""
if [ "$NO_CACHE" = true ]; then
    BUILD_ARGS="$BUILD_ARGS --no-cache"
fi

if [ "$PUSH" = true ]; then
    BUILD_ARGS="$BUILD_ARGS --push"
else
    BUILD_ARGS="$BUILD_ARGS --load"
fi

# 执行构建
case $BUILD_TYPE in
    all)
        echo -e "${BLUE}构建all-in-one镜像...${NC}"
        docker buildx build \
            --platform "$PLATFORMS" \
            --file docker/Dockerfile \
            --tag "${FULL_IMAGE_NAME}:${VERSION}" \
            --tag "${FULL_IMAGE_NAME}:latest" \
            $BUILD_ARGS \
            .
        ;;
    
    backend)
        echo -e "${BLUE}构建backend镜像...${NC}"
        docker buildx build \
            --platform "$PLATFORMS" \
            --file docker/Dockerfile.backend \
            --tag "${FULL_IMAGE_NAME}-backend:${VERSION}" \
            --tag "${FULL_IMAGE_NAME}-backend:latest" \
            $BUILD_ARGS \
            .
        ;;
    
    frontend)
        echo -e "${BLUE}构建frontend镜像...${NC}"
        docker buildx build \
            --platform "$PLATFORMS" \
            --file docker/Dockerfile.frontend \
            --tag "${FULL_IMAGE_NAME}-frontend:${VERSION}" \
            --tag "${FULL_IMAGE_NAME}-frontend:latest" \
            $BUILD_ARGS \
            .
        ;;
    
    *)
        echo -e "${RED}错误: 未知的构建类型 ${BUILD_TYPE}${NC}"
        exit 1
        ;;
esac

# 构建成功
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  构建完成!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "镜像: ${FULL_IMAGE_NAME}:${VERSION}"

if [ "$PUSH" = true ]; then
    echo -e "${GREEN}镜像已推送到仓库${NC}"
else
    echo -e "${YELLOW}镜像已加载到本地Docker${NC}"
    echo -e "运行镜像: ${BLUE}docker run -p 8080:8080 ${FULL_IMAGE_NAME}:${VERSION}${NC}"
fi
#!/bin/bash
# 健康检查脚本

# 检查uni-load-improved主服务
check_main_service() {
    curl -f -s http://localhost:8080/api/v1/health > /dev/null 2>&1
    return $?
}

# 检查gpt-load服务（如果是internal模式）
check_gptload() {
    if [ "$GPT_LOAD_MODE" = "internal" ]; then
        curl -f -s http://localhost:3001/health > /dev/null 2>&1
        return $?
    fi
    return 0
}

# 检查uni-api服务（如果是internal模式）
check_uniapi() {
    if [ "$UNI_API_MODE" = "internal" ]; then
        curl -f -s http://localhost:8000/health > /dev/null 2>&1
        return $?
    fi
    return 0
}

# 执行健康检查
main_status=0
gptload_status=0
uniapi_status=0

check_main_service
main_status=$?

check_gptload
gptload_status=$?

check_uniapi
uniapi_status=$?

# 输出状态
if [ $main_status -eq 0 ]; then
    echo "✓ uni-load-improved: healthy"
else
    echo "✗ uni-load-improved: unhealthy"
fi

if [ "$GPT_LOAD_MODE" = "internal" ]; then
    if [ $gptload_status -eq 0 ]; then
        echo "✓ gpt-load: healthy"
    else
        echo "✗ gpt-load: unhealthy"
    fi
fi

if [ "$UNI_API_MODE" = "internal" ]; then
    if [ $uniapi_status -eq 0 ]; then
        echo "✓ uni-api: healthy"
    else
        echo "✗ uni-api: unhealthy"
    fi
fi

# 主服务必须健康
if [ $main_status -ne 0 ]; then
    exit 1
fi

# 如果是internal模式，相关服务也必须健康
if [ "$GPT_LOAD_MODE" = "internal" ] && [ $gptload_status -ne 0 ]; then
    exit 1
fi

if [ "$UNI_API_MODE" = "internal" ] && [ $uniapi_status -ne 0 ]; then
    exit 1
fi

exit 0
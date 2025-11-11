#!/bin/bash
# 设置Docker相关脚本的执行权限

echo "设置脚本执行权限..."

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 设置执行权限
chmod +x "$SCRIPT_DIR/entrypoint.sh"
chmod +x "$SCRIPT_DIR/healthcheck.sh"
chmod +x "$SCRIPT_DIR/build.sh"
chmod +x "$SCRIPT_DIR/deploy.sh"

echo "✓ entrypoint.sh"
echo "✓ healthcheck.sh"
echo "✓ build.sh"
echo "✓ deploy.sh"

echo ""
echo "所有脚本权限设置完成！"
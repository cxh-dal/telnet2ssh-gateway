#!/bin/bash
# 停止脚本

set -e

echo "正在停止 Telnet to SSH Proxy 服务..."

# 使用docker compose或docker-compose
if docker compose version &> /dev/null 2>&1; then
    docker compose down
else
    docker-compose down
fi

echo "服务已停止"

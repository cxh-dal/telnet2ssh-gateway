#!/bin/bash
# 启动脚本

set -e

echo "========================================"
echo "Telnet to SSH Proxy 启动脚本"
echo "========================================"

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "错误: Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null 2>&1; then
    echo "错误: Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 创建必要的目录
mkdir -p data logs

# 检查配置文件
if [ ! -f "config.yaml" ]; then
    echo "错误: config.yaml 不存在"
    exit 1
fi

echo "正在启动服务..."

# 使用docker compose或docker-compose
if docker compose version &> /dev/null 2>&1; then
    docker compose up -d --build
else
    docker-compose up -d --build
fi

echo ""
echo "========================================"
echo "服务启动成功！"
echo "========================================"
echo ""
echo "查看日志: docker logs -f telnet-ssh-proxy"
echo "查看状态: docker ps"
echo "停止服务: ./stop.sh"
echo "管理映射: docker exec telnet-ssh-proxy python manage.py list"
echo ""

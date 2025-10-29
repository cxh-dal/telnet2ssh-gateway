#!/bin/bash
# 故障排查脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================"
echo "Telnet to SSH Proxy 故障排查工具"
echo "========================================"
echo ""

# 1. 检查Docker
echo -e "${BLUE}[1/8] 检查Docker环境${NC}"
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo -e "${GREEN}✓${NC} Docker已安装: $DOCKER_VERSION"
else
    echo -e "${RED}✗${NC} Docker未安装"
fi
echo ""

# 2. 检查Docker Compose
echo -e "${BLUE}[2/8] 检查Docker Compose${NC}"
if docker compose version &> /dev/null 2>&1; then
    COMPOSE_VERSION=$(docker compose version)
    echo -e "${GREEN}✓${NC} Docker Compose已安装: $COMPOSE_VERSION"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    echo -e "${GREEN}✓${NC} Docker Compose已安装: $COMPOSE_VERSION"
else
    echo -e "${RED}✗${NC} Docker Compose未安装"
fi
echo ""

# 3. 检查配置文件
echo -e "${BLUE}[3/8] 检查配置文件${NC}"
if [ -f "config.yaml" ]; then
    echo -e "${GREEN}✓${NC} config.yaml 存在"
    
    # 检查是否有启用的映射
    ENABLED_COUNT=$(grep -A 3 "enabled: true" config.yaml | wc -l || echo "0")
    if [ "$ENABLED_COUNT" -gt 0 ]; then
        echo -e "${GREEN}✓${NC} 配置文件中有启用的映射"
    else
        echo -e "${YELLOW}!${NC} 警告: 没有启用的端口映射"
    fi
else
    echo -e "${RED}✗${NC} config.yaml 不存在"
fi
echo ""

# 4. 检查容器状态
echo -e "${BLUE}[4/8] 检查容器状态${NC}"
if docker ps --format "{{.Names}}" | grep -q "telnet-ssh-proxy"; then
    echo -e "${GREEN}✓${NC} 容器正在运行"
    
    # 显示容器信息
    echo "容器详情:"
    docker ps --filter "name=telnet-ssh-proxy" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
else
    echo -e "${RED}✗${NC} 容器未运行"
    
    # 检查是否有停止的容器
    if docker ps -a --format "{{.Names}}" | grep -q "telnet-ssh-proxy"; then
        echo -e "${YELLOW}!${NC} 发现已停止的容器"
        docker ps -a --filter "name=telnet-ssh-proxy" --format "table {{.Names}}\t{{.Status}}"
    fi
fi
echo ""

# 5. 检查容器日志
echo -e "${BLUE}[5/8] 检查容器日志${NC}"
if docker ps --format "{{.Names}}" | grep -q "telnet-ssh-proxy"; then
    echo "最近的日志 (最后20行):"
    echo "----------------------------------------"
    docker logs telnet-ssh-proxy --tail 20 2>&1 || echo "无法读取日志"
    echo "----------------------------------------"
    
    # 检查是否有错误
    ERROR_COUNT=$(docker logs telnet-ssh-proxy 2>&1 | grep -i error | wc -l || echo "0")
    if [ "$ERROR_COUNT" -gt 0 ]; then
        echo -e "${YELLOW}!${NC} 发现 $ERROR_COUNT 个错误日志"
    else
        echo -e "${GREEN}✓${NC} 没有发现错误日志"
    fi
else
    echo -e "${YELLOW}!${NC} 容器未运行，无法查看日志"
fi
echo ""

# 6. 检查端口监听
echo -e "${BLUE}[6/8] 检查端口监听${NC}"
if [ -f "config.yaml" ]; then
    # 提取启用的端口
    PORTS=$(grep -B 1 "enabled: true" config.yaml | grep -E "^  [0-9]+:" | sed 's/://g' | tr -d ' ' || echo "")
    
    if [ -n "$PORTS" ]; then
        for port in $PORTS; do
            if netstat -tuln 2>/dev/null | grep -q ":$port " || ss -tuln 2>/dev/null | grep -q ":$port "; then
                echo -e "${GREEN}✓${NC} 端口 $port 正在监听"
            else
                echo -e "${RED}✗${NC} 端口 $port 未监听"
            fi
        done
    else
        echo -e "${YELLOW}!${NC} 没有启用的端口"
    fi
else
    echo -e "${YELLOW}!${NC} 无法检查端口（config.yaml不存在）"
fi
echo ""

# 7. 检查数据目录
echo -e "${BLUE}[7/8] 检查数据目录${NC}"
if [ -d "data" ]; then
    echo -e "${GREEN}✓${NC} data 目录存在"
    if [ -f "data/ssh_host_key" ]; then
        echo -e "${GREEN}✓${NC} SSH主机密钥存在"
    else
        echo -e "${YELLOW}!${NC} SSH主机密钥不存在（首次运行时会自动生成）"
    fi
else
    echo -e "${YELLOW}!${NC} data 目录不存在（首次运行时会自动创建）"
fi

if [ -d "logs" ]; then
    echo -e "${GREEN}✓${NC} logs 目录存在"
    if [ -f "logs/proxy.log" ]; then
        LOG_SIZE=$(du -h logs/proxy.log | cut -f1)
        echo -e "${GREEN}✓${NC} 日志文件存在 (大小: $LOG_SIZE)"
    fi
else
    echo -e "${YELLOW}!${NC} logs 目录不存在（首次运行时会自动创建）"
fi
echo ""

# 8. 运行健康检查
echo -e "${BLUE}[8/8] 运行健康检查${NC}"
if docker ps --format "{{.Names}}" | grep -q "telnet-ssh-proxy"; then
    if docker exec telnet-ssh-proxy python health_check.py 2>/dev/null; then
        echo -e "${GREEN}✓${NC} 健康检查通过"
    else
        echo -e "${RED}✗${NC} 健康检查失败"
    fi
else
    echo -e "${YELLOW}!${NC} 容器未运行，无法执行健康检查"
fi
echo ""

# 总结和建议
echo "========================================"
echo -e "${BLUE}诊断总结和建议${NC}"
echo "========================================"

if ! docker ps --format "{{.Names}}" | grep -q "telnet-ssh-proxy"; then
    echo -e "${YELLOW}建议:${NC}"
    echo "1. 启动服务: ./start.sh 或 make start"
    echo "2. 查看详细日志: docker logs telnet-ssh-proxy"
fi

if [ -f "config.yaml" ]; then
    ENABLED_COUNT=$(grep -A 3 "enabled: true" config.yaml | wc -l || echo "0")
    if [ "$ENABLED_COUNT" -eq 0 ]; then
        echo -e "${YELLOW}建议:${NC}"
        echo "1. 配置端口映射: python manage.py add 4001 <telnet-host> 23"
        echo "2. 或编辑config.yaml启用现有映射"
    fi
fi

echo ""
echo "更多帮助:"
echo "  查看完整日志: docker logs -f telnet-ssh-proxy"
echo "  查看端口映射: docker exec telnet-ssh-proxy python manage.py list"
echo "  重启服务: ./stop.sh && ./start.sh"
echo ""

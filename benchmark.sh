#!/bin/bash
# 性能测试脚本 - 测试代理服务的并发性能

set -e

# 默认配置
HOST="localhost"
PORT="4001"
USERNAME="ritts"
PASSWORD="ritts"
CONCURRENT=10
DURATION=60

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--host)
            HOST="$2"
            shift 2
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -c|--concurrent)
            CONCURRENT="$2"
            shift 2
            ;;
        -d|--duration)
            DURATION="$2"
            shift 2
            ;;
        *)
            echo "未知参数: $1"
            echo "用法: $0 [-h HOST] [-p PORT] [-c CONCURRENT] [-d DURATION]"
            exit 1
            ;;
    esac
done

echo "========================================"
echo "Telnet to SSH Proxy 性能测试"
echo "========================================"
echo "目标: $HOST:$PORT"
echo "并发连接数: $CONCURRENT"
echo "测试时长: ${DURATION}秒"
echo "========================================"
echo ""

# 检查依赖
if ! command -v sshpass &> /dev/null; then
    echo -e "${YELLOW}警告: 未安装sshpass，某些测试可能无法运行${NC}"
fi

# 测试单个连接
echo -e "${GREEN}测试1: 单连接延迟${NC}"
START_TIME=$(date +%s.%N)
timeout 5 sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p "$PORT" "$USERNAME@$HOST" "exit" 2>/dev/null || true
END_TIME=$(date +%s.%N)
LATENCY=$(echo "$END_TIME - $START_TIME" | bc)
echo "连接延迟: ${LATENCY}秒"
echo ""

# 测试并发连接
echo -e "${GREEN}测试2: 并发连接测试${NC}"
SUCCESS=0
FAILED=0

test_connection() {
    if timeout 10 sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p "$PORT" "$USERNAME@$HOST" "exit" &>/dev/null; then
        echo "1"
    else
        echo "0"
    fi
}

echo "启动 $CONCURRENT 个并发连接..."
START=$(date +%s)

for i in $(seq 1 $CONCURRENT); do
    result=$(test_connection) &
    if [ "$result" == "1" ]; then
        ((SUCCESS++))
    else
        ((FAILED++))
    fi
done

# 等待所有后台任务完成
wait

END=$(date +%s)
ELAPSED=$((END - START))

echo ""
echo "测试结果:"
echo "  成功: $SUCCESS"
echo "  失败: $FAILED"
echo "  耗时: ${ELAPSED}秒"
echo ""

# 测试持续负载
echo -e "${GREEN}测试3: 持续负载测试 (${DURATION}秒)${NC}"
echo "正在运行..."

TEST_START=$(date +%s)
TEST_END=$((TEST_START + DURATION))
CONNECTION_COUNT=0

while [ $(date +%s) -lt $TEST_END ]; do
    for i in $(seq 1 $CONCURRENT); do
        (timeout 5 sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p "$PORT" "$USERNAME@$HOST" "exit" &>/dev/null && echo "OK") &
    done
    wait
    CONNECTION_COUNT=$((CONNECTION_COUNT + CONCURRENT))
    
    # 显示进度
    CURRENT=$(date +%s)
    PROGRESS=$((CURRENT - TEST_START))
    echo -ne "\r进度: ${PROGRESS}/${DURATION}秒, 完成连接: $CONNECTION_COUNT"
    
    sleep 1
done

echo ""
echo ""
echo "持续负载测试结果:"
echo "  总连接数: $CONNECTION_COUNT"
echo "  平均QPS: $(echo "scale=2; $CONNECTION_COUNT / $DURATION" | bc)"
echo ""

echo "========================================"
echo -e "${GREEN}测试完成！${NC}"
echo "========================================"

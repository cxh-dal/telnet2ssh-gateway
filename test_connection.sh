#!/bin/bash
# 测试连接脚本

set -e

# 默认值
HOST="localhost"
PORT="4001"
USERNAME="ritts"
PASSWORD="ritts"

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
        -u|--username)
            USERNAME="$2"
            shift 2
            ;;
        --password)
            PASSWORD="$2"
            shift 2
            ;;
        *)
            echo "未知参数: $1"
            echo "用法: $0 [-h HOST] [-p PORT] [-u USERNAME] [--password PASSWORD]"
            exit 1
            ;;
    esac
done

echo "========================================"
echo "测试SSH连接到代理服务器"
echo "========================================"
echo "主机: $HOST"
echo "端口: $PORT"
echo "用户: $USERNAME"
echo "========================================"
echo ""

# 检查sshpass是否安装
if command -v sshpass &> /dev/null; then
    echo "使用sshpass连接..."
    sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p "$PORT" "$USERNAME@$HOST"
else
    echo "提示: 安装sshpass可以自动输入密码"
    echo "手动连接: ssh -p $PORT $USERNAME@$HOST"
    echo "密码: $PASSWORD"
    echo ""
    ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p "$PORT" "$USERNAME@$HOST"
fi

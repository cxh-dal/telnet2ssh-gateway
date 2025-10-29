#!/usr/bin/env python3
"""
健康检查脚本
检查代理服务是否正常运行
"""

import socket
import sys
import yaml
import time


def check_port(port: int, timeout: int = 5) -> bool:
    """检查端口是否可连接"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result == 0
    except Exception as e:
        return False


def main():
    """主函数"""
    config_file = 'config.yaml'
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"错误: 无法加载配置文件: {e}")
        sys.exit(1)
    
    # 获取所有启用的端口
    enabled_ports = []
    mappings = config.get('mappings', {})
    
    for port, mapping in mappings.items():
        if mapping.get('enabled', False) and mapping.get('host'):
            enabled_ports.append(int(port))
    
    if not enabled_ports:
        print("警告: 没有启用的端口映射")
        sys.exit(0)
    
    # 检查每个端口
    all_healthy = True
    unhealthy_ports = []
    
    for port in enabled_ports:
        if check_port(port):
            print(f"✓ 端口 {port} 健康")
        else:
            print(f"✗ 端口 {port} 不可用")
            all_healthy = False
            unhealthy_ports.append(port)
    
    if all_healthy:
        print("\n所有服务健康运行")
        sys.exit(0)
    else:
        print(f"\n{len(unhealthy_ports)} 个服务不可用: {unhealthy_ports}")
        sys.exit(1)


if __name__ == '__main__':
    main()

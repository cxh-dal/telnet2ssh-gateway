#!/usr/bin/env python3
"""
健康检查脚本
检查代理服务是否正常运行
"""

import socket
import sys
import yaml
import time
import os


def check_port(port: int, timeout: int = 5) -> bool:
    """检查端口是否可连接，并发送最小SSH banner避免服务端错误日志"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex(('127.0.0.1', port))
        if result != 0:
            try:
                sock.close()
            except:
                pass
            return False

        # 连接成功后，发送一个最小的 SSH 客户端标识，
        # 避免服务端 Paramiko 因读取不到 banner 而报错。
        try:
            sock.settimeout(0.5)
            sock.sendall(b"SSH-2.0-HealthCheck\r\n")
            # 读取少量数据（若有），以完成一次轻量交互
            try:
                _ = sock.recv(256)
            except Exception:
                pass
        except Exception:
            # 发送/接收失败不影响健康结论
            pass
        finally:
            try:
                sock.close()
            except:
                pass
        return True
    except Exception:
        return False


def main():
    """主函数"""
    # 允许通过环境变量指定配置文件，默认 config.yaml
    config_file = os.environ.get('CONFIG_FILE', 'config.yaml')

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
    except Exception as e:
        print(f"错误: 无法加载配置文件: {e}")
        sys.exit(1)

    # 健康检查开关
    hc_cfg = config.get('health_check') or {}
    if not hc_cfg.get('enabled', True):
        print("健康检查已禁用，跳过")
        sys.exit(0)

    # 获取所有启用的端口
    enabled_ports = []
    mappings = config.get('mappings', {}) or {}

    for port, mapping in mappings.items():
        if mapping.get('enabled', False) and mapping.get('host'):
            enabled_ports.append(int(port))

    if not enabled_ports:
        print("警告: 没有启用的端口映射")
        sys.exit(0)

    # 读取超时配置（仅影响 socket 检测超时）
    timeout = int(hc_cfg.get('timeout', 5))

    # 检查每个端口
    all_healthy = True
    unhealthy_ports = []

    for port in enabled_ports:
        if check_port(port, timeout=timeout):
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

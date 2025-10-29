#!/usr/bin/env python3
"""
监控脚本 - 持续监控代理服务状态
"""

import socket
import yaml
import time
import sys
import logging
from datetime import datetime
from typing import Dict, List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProxyMonitor:
    """代理服务监控器"""
    
    def __init__(self, config_file: str = 'config.yaml'):
        self.config_file = config_file
        self.config = None
        self.stats: Dict[int, Dict] = {}
        
    def load_config(self):
        """加载配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            sys.exit(1)
    
    def check_port(self, port: int, timeout: int = 5) -> bool:
        """检查端口是否可连接"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            return result == 0
        except:
            return False
    
    def get_enabled_ports(self) -> List[int]:
        """获取所有启用的端口"""
        ports = []
        mappings = self.config.get('mappings', {})
        for port, mapping in mappings.items():
            if mapping.get('enabled', False) and mapping.get('host'):
                ports.append(int(port))
        return sorted(ports)
    
    def check_all_ports(self) -> Dict[int, bool]:
        """检查所有端口状态"""
        results = {}
        ports = self.get_enabled_ports()
        
        for port in ports:
            results[port] = self.check_port(port)
            
            # 更新统计信息
            if port not in self.stats:
                self.stats[port] = {
                    'total_checks': 0,
                    'success_count': 0,
                    'fail_count': 0,
                    'last_status': None,
                    'last_check': None,
                    'consecutive_fails': 0
                }
            
            self.stats[port]['total_checks'] += 1
            self.stats[port]['last_check'] = datetime.now()
            self.stats[port]['last_status'] = results[port]
            
            if results[port]:
                self.stats[port]['success_count'] += 1
                self.stats[port]['consecutive_fails'] = 0
            else:
                self.stats[port]['fail_count'] += 1
                self.stats[port]['consecutive_fails'] += 1
        
        return results
    
    def print_status(self, results: Dict[int, bool]):
        """打印状态报告"""
        mappings = self.config.get('mappings', {})
        
        print("\n" + "="*80)
        print(f"监控报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # 显示当前状态
        healthy_count = sum(1 for v in results.values() if v)
        total_count = len(results)
        
        print(f"\n总体状态: {healthy_count}/{total_count} 服务健康")
        print(f"\n{'端口':<8} {'状态':<10} {'目标地址':<30} {'描述':<20}")
        print("-"*80)
        
        for port in sorted(results.keys()):
            status = "✓ 健康" if results[port] else "✗ 异常"
            mapping = mappings.get(str(port), {})
            target = f"{mapping.get('host', '')}:{mapping.get('port', 23)}"
            desc = mapping.get('description', '')
            
            # 连续失败警告
            if self.stats[port]['consecutive_fails'] >= 3:
                status += f" (连续失败{self.stats[port]['consecutive_fails']}次)"
            
            print(f"{port:<8} {status:<10} {target:<30} {desc:<20}")
        
        # 显示统计信息
        if self.stats:
            print("\n统计信息:")
            print("-"*80)
            for port in sorted(self.stats.keys()):
                stat = self.stats[port]
                success_rate = (stat['success_count'] / stat['total_checks'] * 100) if stat['total_checks'] > 0 else 0
                print(f"端口 {port}: "
                      f"成功率 {success_rate:.1f}% "
                      f"({stat['success_count']}/{stat['total_checks']}) "
                      f"失败 {stat['fail_count']}次")
        
        print("="*80)
    
    def run_once(self):
        """执行一次检查"""
        self.load_config()
        results = self.check_all_ports()
        self.print_status(results)
        
        # 返回是否所有服务都健康
        return all(results.values())
    
    def run_continuous(self, interval: int = 30):
        """持续监控"""
        logger.info(f"开始持续监控，检查间隔: {interval}秒")
        logger.info("按 Ctrl+C 停止监控")
        
        try:
            while True:
                self.load_config()
                results = self.check_all_ports()
                self.print_status(results)
                
                # 检查是否有需要告警的情况
                for port, stat in self.stats.items():
                    if stat['consecutive_fails'] >= 3:
                        logger.warning(f"告警: 端口 {port} 连续失败 {stat['consecutive_fails']} 次!")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("\n监控已停止")
            self.print_summary()
    
    def print_summary(self):
        """打印汇总统计"""
        if not self.stats:
            return
        
        print("\n" + "="*80)
        print("监控汇总统计")
        print("="*80)
        
        for port in sorted(self.stats.keys()):
            stat = self.stats[port]
            if stat['total_checks'] > 0:
                success_rate = stat['success_count'] / stat['total_checks'] * 100
                print(f"\n端口 {port}:")
                print(f"  总检查次数: {stat['total_checks']}")
                print(f"  成功次数: {stat['success_count']}")
                print(f"  失败次数: {stat['fail_count']}")
                print(f"  成功率: {success_rate:.2f}%")
                if stat['last_check']:
                    print(f"  最后检查: {stat['last_check'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("="*80)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Telnet to SSH Proxy 监控工具')
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='配置文件路径'
    )
    parser.add_argument(
        '--continuous',
        action='store_true',
        help='持续监控模式'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=30,
        help='持续监控的检查间隔（秒）'
    )
    
    args = parser.parse_args()
    
    monitor = ProxyMonitor(args.config)
    
    if args.continuous:
        monitor.run_continuous(args.interval)
    else:
        all_healthy = monitor.run_once()
        sys.exit(0 if all_healthy else 1)


if __name__ == '__main__':
    main()

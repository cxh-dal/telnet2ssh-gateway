#!/usr/bin/env python3
"""
Telnet to SSH Proxy 管理工具
用于管理端口映射配置
"""

import yaml
import sys
import argparse
from typing import Dict, Optional


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = 'config.yaml'):
        self.config_file = config_file
        self.config = None
        
    def load(self):
        """加载配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            print(f"错误: 无法加载配置文件: {e}")
            sys.exit(1)
    
    def save(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            print(f"配置已保存到 {self.config_file}")
        except Exception as e:
            print(f"错误: 无法保存配置文件: {e}")
            sys.exit(1)
    
    def list_mappings(self):
        """列出所有端口映射"""
        print("\n端口映射列表:")
        print("="*80)
        print(f"{'端口':<8} {'状态':<8} {'Telnet地址':<30} {'描述':<20}")
        print("-"*80)
        
        mappings = self.config.get('mappings', {})
        for port in sorted(mappings.keys(), key=int):
            mapping = mappings[port]
            status = "启用" if mapping.get('enabled', False) else "禁用"
            telnet_addr = f"{mapping.get('host', '')}:{mapping.get('port', 23)}"
            if not mapping.get('host'):
                telnet_addr = "未配置"
            desc = mapping.get('description', '')
            
            print(f"{port:<8} {status:<8} {telnet_addr:<30} {desc:<20}")
        
        print("="*80)
        print()
    
    def add_mapping(self, ssh_port: int, telnet_host: str, telnet_port: int, 
                   description: str = "", enabled: bool = True):
        """添加或更新端口映射"""
        if ssh_port < 4001 or ssh_port > 4032:
            print(f"错误: SSH端口必须在4001-4032范围内")
            return False
        
        mappings = self.config.get('mappings', {})
        
        mappings[ssh_port] = {
            'host': telnet_host,
            'port': telnet_port,
            'enabled': enabled,
            'description': description
        }
        
        self.config['mappings'] = mappings
        self.save()
        
        status = "启用" if enabled else "禁用"
        print(f"成功添加映射: SSH端口 {ssh_port} -> Telnet {telnet_host}:{telnet_port} ({status})")
        return True
    
    def remove_mapping(self, ssh_port: int):
        """移除端口映射（设置为未配置状态）"""
        mappings = self.config.get('mappings', {})
        
        if ssh_port not in mappings:
            print(f"错误: 端口 {ssh_port} 的映射不存在")
            return False
        
        mappings[ssh_port] = {
            'host': '',
            'port': 23,
            'enabled': False,
            'description': f'映射{ssh_port - 4000}'
        }
        
        self.save()
        print(f"已移除端口 {ssh_port} 的映射配置")
        return True
    
    def enable_mapping(self, ssh_port: int):
        """启用端口映射"""
        mappings = self.config.get('mappings', {})
        
        if ssh_port not in mappings:
            print(f"错误: 端口 {ssh_port} 的映射不存在")
            return False
        
        if not mappings[ssh_port].get('host'):
            print(f"错误: 端口 {ssh_port} 未配置Telnet目标地址")
            return False
        
        mappings[ssh_port]['enabled'] = True
        self.save()
        print(f"已启用端口 {ssh_port} 的映射")
        return True
    
    def disable_mapping(self, ssh_port: int):
        """禁用端口映射"""
        mappings = self.config.get('mappings', {})
        
        if ssh_port not in mappings:
            print(f"错误: 端口 {ssh_port} 的映射不存在")
            return False
        
        mappings[ssh_port]['enabled'] = False
        self.save()
        print(f"已禁用端口 {ssh_port} 的映射")
        return True
    
    def show_mapping(self, ssh_port: int):
        """显示特定端口的映射详情"""
        mappings = self.config.get('mappings', {})
        
        if ssh_port not in mappings:
            print(f"错误: 端口 {ssh_port} 的映射不存在")
            return False
        
        mapping = mappings[ssh_port]
        print(f"\n端口 {ssh_port} 的映射详情:")
        print("="*50)
        print(f"SSH端口: {ssh_port}")
        print(f"Telnet地址: {mapping.get('host', '未配置')}")
        print(f"Telnet端口: {mapping.get('port', 23)}")
        print(f"状态: {'启用' if mapping.get('enabled', False) else '禁用'}")
        print(f"描述: {mapping.get('description', '')}")
        print("="*50)
        print()
        return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Telnet to SSH Proxy 管理工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 列出所有映射
  python manage.py list

  # 添加新映射
  python manage.py add 4001 192.168.1.100 23 --description "设备1"

  # 启用映射
  python manage.py enable 4001

  # 禁用映射
  python manage.py disable 4001

  # 删除映射
  python manage.py remove 4001

  # 查看映射详情
  python manage.py show 4001
        """
    )
    
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='配置文件路径 (默认: config.yaml)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # list命令
    subparsers.add_parser('list', help='列出所有端口映射')
    
    # add命令
    add_parser = subparsers.add_parser('add', help='添加或更新端口映射')
    add_parser.add_argument('ssh_port', type=int, help='SSH端口 (4001-4032)')
    add_parser.add_argument('telnet_host', help='Telnet主机地址')
    add_parser.add_argument('telnet_port', type=int, help='Telnet端口')
    add_parser.add_argument('--description', default='', help='描述信息')
    add_parser.add_argument('--disabled', action='store_true', help='添加后不启用')
    
    # remove命令
    remove_parser = subparsers.add_parser('remove', help='移除端口映射')
    remove_parser.add_argument('ssh_port', type=int, help='SSH端口')
    
    # enable命令
    enable_parser = subparsers.add_parser('enable', help='启用端口映射')
    enable_parser.add_argument('ssh_port', type=int, help='SSH端口')
    
    # disable命令
    disable_parser = subparsers.add_parser('disable', help='禁用端口映射')
    disable_parser.add_argument('ssh_port', type=int, help='SSH端口')
    
    # show命令
    show_parser = subparsers.add_parser('show', help='显示端口映射详情')
    show_parser.add_argument('ssh_port', type=int, help='SSH端口')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    manager = ConfigManager(args.config)
    manager.load()
    
    if args.command == 'list':
        manager.list_mappings()
    
    elif args.command == 'add':
        manager.add_mapping(
            args.ssh_port,
            args.telnet_host,
            args.telnet_port,
            args.description,
            not args.disabled
        )
    
    elif args.command == 'remove':
        manager.remove_mapping(args.ssh_port)
    
    elif args.command == 'enable':
        manager.enable_mapping(args.ssh_port)
    
    elif args.command == 'disable':
        manager.disable_mapping(args.ssh_port)
    
    elif args.command == 'show':
        manager.show_mapping(args.ssh_port)


if __name__ == '__main__':
    main()

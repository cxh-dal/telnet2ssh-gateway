#!/usr/bin/env python3
"""
Telnet to SSH Proxy Server
将SSH连接代理到Telnet后端
"""

import socket
import paramiko
import threading
import logging
import select
import sys
import time
from typing import Dict, Tuple
import yaml
import os

logger = logging.getLogger(__name__)


class TelnetClient:
    """Telnet客户端，用于连接到Telnet后端"""
    
    def __init__(self, host: str, port: int, timeout: int = 10):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock = None
        
    def connect(self) -> bool:
        """连接到Telnet服务器"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(self.timeout)
            self.sock.connect((self.host, self.port))
            logger.info(f"成功连接到Telnet服务器 {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"连接Telnet服务器失败 {self.host}:{self.port}: {e}")
            return False
    
    def send(self, data: bytes) -> bool:
        """发送数据到Telnet服务器"""
        try:
            if self.sock:
                self.sock.sendall(data)
                return True
        except Exception as e:
            logger.error(f"发送数据到Telnet服务器失败: {e}")
        return False
    
    def recv(self, size: int = 4096) -> bytes:
        """从Telnet服务器接收数据"""
        try:
            if self.sock:
                return self.sock.recv(size)
        except Exception as e:
            logger.debug(f"从Telnet服务器接收数据失败: {e}")
        return b''
    
    def close(self):
        """关闭连接"""
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.sock = None


class SSHServerHandler(paramiko.ServerInterface):
    """SSH服务器处理器"""
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.event = threading.Event()
    
    def check_auth_password(self, username: str, password: str) -> int:
        """验证用户名和密码"""
        if username == self.username and password == self.password:
            logger.info(f"用户 {username} 认证成功")
            return paramiko.AUTH_SUCCESSFUL
        logger.warning(f"用户 {username} 认证失败")
        return paramiko.AUTH_FAILED
    
    def check_channel_request(self, kind: str, chanid: int) -> int:
        """处理channel请求"""
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    
    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        """处理PTY请求"""
        return True
    
    def check_channel_shell_request(self, channel):
        """处理Shell请求"""
        self.event.set()
        return True
    
    def check_channel_exec_request(self, channel, command):
        """处理命令执行请求"""
        self.event.set()
        return True


class ProxySession:
    """代理会话，处理SSH和Telnet之间的数据转发"""
    
    def __init__(self, ssh_channel, telnet_host: str, telnet_port: int):
        self.ssh_channel = ssh_channel
        self.telnet_host = telnet_host
        self.telnet_port = telnet_port
        self.telnet_client = None
        self.running = False
        
    def start(self):
        """启动代理会话"""
        # 连接到Telnet后端
        self.telnet_client = TelnetClient(self.telnet_host, self.telnet_port)
        if not self.telnet_client.connect():
            try:
                self.ssh_channel.send(f"错误: 无法连接到Telnet服务器 {self.telnet_host}:{self.telnet_port}\r\n".encode())
                self.ssh_channel.close()
            except:
                pass
            return
        
        self.running = True
        
        # 启动双向数据转发线程
        ssh_to_telnet = threading.Thread(target=self._forward_ssh_to_telnet)
        telnet_to_ssh = threading.Thread(target=self._forward_telnet_to_ssh)
        
        ssh_to_telnet.daemon = True
        telnet_to_ssh.daemon = True
        
        ssh_to_telnet.start()
        telnet_to_ssh.start()
        
        # 等待会话结束
        ssh_to_telnet.join()
        telnet_to_ssh.join()
        
        self.cleanup()
    
    def _forward_ssh_to_telnet(self):
        """转发SSH数据到Telnet"""
        try:
            while self.running:
                if self.ssh_channel.recv_ready():
                    data = self.ssh_channel.recv(4096)
                    if len(data) == 0:
                        break
                    if not self.telnet_client.send(data):
                        break
                else:
                    time.sleep(0.01)
        except Exception as e:
            logger.debug(f"SSH到Telnet转发异常: {e}")
        finally:
            self.running = False
    
    def _forward_telnet_to_ssh(self):
        """转发Telnet数据到SSH"""
        try:
            while self.running:
                # 使用select检查是否有数据可读
                if self.telnet_client.sock:
                    ready = select.select([self.telnet_client.sock], [], [], 0.1)
                    if ready[0]:
                        data = self.telnet_client.recv(4096)
                        if len(data) == 0:
                            break
                        try:
                            self.ssh_channel.send(data)
                        except:
                            break
        except Exception as e:
            logger.debug(f"Telnet到SSH转发异常: {e}")
        finally:
            self.running = False
    
    def cleanup(self):
        """清理资源"""
        self.running = False
        if self.telnet_client:
            self.telnet_client.close()
        try:
            self.ssh_channel.close()
        except:
            pass


class SSHProxyServer:
    """SSH代理服务器"""
    
    def __init__(self, port: int, telnet_host: str, telnet_port: int, 
                 username: str, password: str, host_key):
        self.port = port
        self.telnet_host = telnet_host
        self.telnet_port = telnet_port
        self.username = username
        self.password = password
        self.host_key = host_key
        self.sock = None
        self.running = False
        
    def start(self):
        """启动SSH服务器"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(('0.0.0.0', self.port))
            self.sock.listen(100)
            self.running = True
            
            logger.info(f"SSH服务器在端口 {self.port} 启动，映射到 {self.telnet_host}:{self.telnet_port}")
            
            while self.running:
                try:
                    self.sock.settimeout(1.0)
                    client, addr = self.sock.accept()
                    logger.info(f"接受来自 {addr} 的SSH连接，端口 {self.port}")
                    
                    # 在新线程中处理客户端连接
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client, addr)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        logger.error(f"接受连接时出错: {e}")
                    
        except Exception as e:
            logger.error(f"启动SSH服务器失败，端口 {self.port}: {e}")
        finally:
            self.stop()
    
    def _handle_client(self, client_socket, addr):
        """处理客户端连接"""
        transport = None
        try:
            transport = paramiko.Transport(client_socket)
            transport.add_server_key(self.host_key)
            
            server = SSHServerHandler(self.username, self.password)
            transport.start_server(server=server)
            
            # 等待客户端建立channel
            channel = transport.accept(20)
            if channel is None:
                logger.warning("客户端未能建立channel")
                return
            
            # 等待shell或exec请求
            server.event.wait(10)
            if not server.event.is_set():
                logger.warning("客户端未请求shell或命令执行")
                channel.close()
                return
            
            # 启动代理会话
            logger.info(f"启动代理会话: SSH端口{self.port} -> Telnet {self.telnet_host}:{self.telnet_port}")
            session = ProxySession(channel, self.telnet_host, self.telnet_port)
            session.start()
            
        except Exception as e:
            # 对健康检查或非SSH探测导致的 banner 错误降级为调试日志
            msg = str(e)
            if 'Error reading SSH protocol banner' in msg:
                logger.debug("收到非SSH/健康检查短连接，已忽略")
            else:
                logger.error(f"处理客户端连接时出错: {e}")
        finally:
            try:
                if transport:
                    transport.close()
            except:
                pass
    
    def stop(self):
        """停止SSH服务器"""
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except:
                pass


class ProxyManager:
    """代理管理器，管理所有的SSH代理服务器"""
    
    def __init__(self, config_file: str = 'config.yaml'):
        self.config_file = config_file
        self.config = None
        self.servers: Dict[int, SSHProxyServer] = {}
        self.server_threads: Dict[int, threading.Thread] = {}
        self.host_key = None
        self.running = False
        
    def load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            logger.info(f"配置文件加载成功: {self.config_file}")
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            raise
        
    def setup_host_key(self):
        """设置SSH主机密钥"""
        host_key_file = self.config['ssh'].get('host_key', 'ssh_host_key')
        
        # 确保目录存在
        os.makedirs(os.path.dirname(host_key_file) or '.', exist_ok=True)
        
        if os.path.exists(host_key_file):
            try:
                self.host_key = paramiko.RSAKey.from_private_key_file(host_key_file)
                logger.info(f"加载SSH主机密钥: {host_key_file}")
            except Exception as e:
                logger.warning(f"加载主机密钥失败: {e}，将生成新密钥")
                self.host_key = None
        
        if not self.host_key:
            logger.info("生成新的SSH主机密钥...")
            self.host_key = paramiko.RSAKey.generate(2048)
            self.host_key.write_private_key_file(host_key_file)
            logger.info(f"SSH主机密钥已保存: {host_key_file}")
    
    def start(self):
        """启动所有配置的代理服务器"""
        self.load_config()
        self.setup_host_key()
        
        username = self.config['ssh']['username']
        password = self.config['ssh']['password']
        
        # 启动每个已启用的映射
        for port, mapping in self.config['mappings'].items():
            port = int(port)
            if mapping.get('enabled', False) and mapping.get('host'):
                telnet_host = mapping['host']
                telnet_port = mapping.get('port', 23)
                
                server = SSHProxyServer(
                    port=port,
                    telnet_host=telnet_host,
                    telnet_port=telnet_port,
                    username=username,
                    password=password,
                    host_key=self.host_key
                )
                
                thread = threading.Thread(target=server.start)
                thread.daemon = True
                thread.start()
                
                self.servers[port] = server
                self.server_threads[port] = thread
                
                logger.info(f"启动代理: SSH端口{port} -> Telnet {telnet_host}:{telnet_port}")
        
        if not self.servers:
            logger.warning("没有启用的端口映射！请编辑config.yaml启用映射")
        
        self.running = True
        
        # 保持主线程运行
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("收到中断信号，正在停止...")
            self.stop()
    
    def stop(self):
        """停止所有代理服务器"""
        self.running = False
        for port, server in self.servers.items():
            logger.info(f"停止端口 {port} 的代理服务器")
            server.stop()
        self.servers.clear()
        self.server_threads.clear()


def setup_logging(config: dict):
    """设置日志"""
    log_config = config.get('logging', {})
    log_level = getattr(logging, log_config.get('level', 'INFO'))
    log_file = log_config.get('file')
    
    # 创建日志目录
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # 配置日志格式
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_file:
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=log_config.get('max_bytes', 10485760),
            backupCount=log_config.get('backup_count', 5)
        )
        handlers.append(file_handler)
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=handlers
    )

    # 降低 Paramiko 在握手阶段的噪音日志，避免健康检查短连接刷屏
    # 使用 CRITICAL 屏蔽其内部 Transport 线程的 ERROR 堆栈
    logging.getLogger("paramiko").setLevel(logging.CRITICAL)
    logging.getLogger("paramiko.transport").setLevel(logging.CRITICAL)



def main():
    """主函数"""
    config_file = os.environ.get('CONFIG_FILE', 'config.yaml')
    
    # 先加载配置以设置日志
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        setup_logging(config)
    except Exception as e:
        logging.basicConfig(level=logging.INFO)
        logger.error(f"加载配置文件失败: {e}")
        return
    
    logger.info("="*50)
    logger.info("Telnet to SSH Proxy Server 启动中...")
    logger.info("="*50)
    
    manager = ProxyManager(config_file)
    manager.start()


if __name__ == '__main__':
    main()

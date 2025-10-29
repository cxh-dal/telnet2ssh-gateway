# Telnet to SSH Proxy

🔒 将SSH连接透明代理到Telnet后端设备的安全解决方案

## 📋 项目简介

Telnet to SSH Proxy 是一个轻量级的代理服务，它允许用户通过安全的SSH协议连接到只支持Telnet的设备。该项目解决了网络安全要求禁止明文协议，但设备不支持SSH的问题。

### ✨ 主要特性

- 🔄 **实时双向透明转发**: SSH和Telnet会话数据无缝流动，支持所有控制字符和原始字节数据
- 🚀 **高并发和稳定性**: 支持多用户同时连接不同的Telnet后端
- 🔌 **端口映射**: 基于端口的一对一映射，默认支持4001-4032共32个端口
- 🐳 **Docker容器化**: 提供完整的Docker部署方案，一键启动
- 🛠️ **便捷管理**: 提供命令行工具管理端口映射
- 💚 **健康检查**: 内置健康检查和自动重启功能
- 🆓 **开源免费**: MIT许可证，可商业使用

## 🏗️ 架构说明

```
用户 (SSH客户端)  <--SSH加密-->  代理服务器  <--Telnet明文-->  后端设备
                              (端口4001-4032)              (Telnet设备)
```

## 🚀 快速开始

### 前置要求

- Docker 20.10+
- Docker Compose 1.29+

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd telnet-ssh-proxy
```

2. **配置端口映射**

编辑 `config.yaml` 文件，配置您的端口映射：

```yaml
mappings:
  4001:
    host: "192.168.1.100"  # Telnet设备IP
    port: 23                # Telnet端口
    enabled: true           # 启用此映射
    description: "交换机1"
  4002:
    host: "192.168.1.101"
    port: 23
    enabled: true
    description: "路由器1"
```

或使用命令行工具配置：

```bash
# 添加映射
python manage.py add 4001 192.168.1.100 23 --description "交换机1"

# 查看所有映射
python manage.py list
```

3. **启动服务**

```bash
./start.sh
```

或手动启动：

```bash
docker-compose up -d --build
```

4. **验证服务**

```bash
# 查看运行状态
docker ps

# 查看日志
docker logs -f telnet-ssh-proxy

# 健康检查
docker exec telnet-ssh-proxy python health_check.py
```

## 📖 使用说明

### 连接到代理服务

使用任何SSH客户端连接到配置的端口：

```bash
# 使用SSH连接 (默认用户名和密码都是 ritts)
ssh -p 4001 ritts@your-proxy-server-ip

# 或使用密码参数
sshpass -p ritts ssh -p 4001 ritts@your-proxy-server-ip
```

连接成功后，您将自动连接到配置的Telnet后端设备。

### 管理端口映射

使用 `manage.py` 脚本管理端口映射：

```bash
# 在容器内执行
docker exec telnet-ssh-proxy python manage.py [command]

# 或直接在宿主机执行
python manage.py [command]
```

#### 可用命令

**列出所有映射**
```bash
python manage.py list
```

**添加/更新映射**
```bash
python manage.py add <SSH端口> <Telnet主机> <Telnet端口> --description "描述"

# 示例
python manage.py add 4001 192.168.1.100 23 --description "交换机1"
```

**查看映射详情**
```bash
python manage.py show 4001
```

**启用映射**
```bash
python manage.py enable 4001
```

**禁用映射**
```bash
python manage.py disable 4001
```

**删除映射**
```bash
python manage.py remove 4001
```

### 配置文件说明

`config.yaml` 主要配置项：

```yaml
# SSH服务器配置
ssh:
  host: "0.0.0.0"           # 监听地址
  username: "ritts"         # SSH用户名
  password: "ritts"         # SSH密码
  host_key: "/app/data/ssh_host_key"  # SSH主机密钥路径

# 端口映射配置
mappings:
  4001:                      # SSH监听端口
    host: "192.168.1.100"    # Telnet目标地址
    port: 23                 # Telnet目标端口
    enabled: true            # 是否启用
    description: "设备1"     # 描述信息

# 日志配置
logging:
  level: "INFO"                        # 日志级别
  file: "/app/logs/proxy.log"          # 日志文件
  max_bytes: 10485760                  # 单个日志文件大小(10MB)
  backup_count: 5                      # 保留日志文件数量

# 健康检查配置
health_check:
  enabled: true              # 启用健康检查
  interval: 30               # 检查间隔(秒)
  timeout: 5                 # 超时时间(秒)
```

## 🔧 高级配置

### 修改SSH认证

编辑 `config.yaml`:

```yaml
ssh:
  username: "your_username"
  password: "your_password"
```

### 自定义端口范围

如需使用4001-4032之外的端口，需要：

1. 修改 `config.yaml` 添加新端口配置
2. 修改 `docker-compose.yml` 暴露新端口
3. 重启服务

### 查看日志

```bash
# 实时查看日志
docker logs -f telnet-ssh-proxy

# 查看日志文件
tail -f logs/proxy.log
```

### 持久化数据

数据和日志通过Docker卷挂载到宿主机：

- `./data` - SSH主机密钥等数据
- `./logs` - 日志文件

## 🔍 故障排查

### 服务无法启动

1. 检查Docker和Docker Compose是否正确安装
2. 检查端口是否被占用：`netstat -tuln | grep 400`
3. 查看容器日志：`docker logs telnet-ssh-proxy`

### 无法连接到SSH端口

1. 检查防火墙规则
2. 确认端口映射已启用：`python manage.py list`
3. 检查Telnet后端是否可达：`telnet <backend-ip> 23`

### 连接后无响应

1. 检查Telnet后端设备是否正常
2. 查看代理日志是否有错误
3. 验证网络连通性

### 健康检查失败

```bash
# 手动执行健康检查
docker exec telnet-ssh-proxy python health_check.py

# 查看具体错误信息
docker logs telnet-ssh-proxy | grep -i error
```

## 📊 监控和维护

### 健康检查

Docker自动执行健康检查，可通过以下方式查看：

```bash
# 查看容器健康状态
docker ps

# 手动执行健康检查
docker exec telnet-ssh-proxy python health_check.py
```

### 重启策略

Docker Compose配置为 `restart: unless-stopped`，服务异常时会自动重启。

### 日志轮转

日志自动轮转，单个文件最大10MB，保留5个历史文件。

## 🏗️ 开发指南

### 本地开发

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 运行代理服务
python proxy_server.py

# 运行管理工具
python manage.py list
```

### 项目结构

```
.
├── proxy_server.py      # 主代理服务器
├── manage.py            # 管理工具
├── health_check.py      # 健康检查脚本
├── config.yaml          # 配置文件
├── requirements.txt     # Python依赖
├── Dockerfile           # Docker镜像构建文件
├── docker-compose.yml   # Docker Compose配置
├── start.sh             # 启动脚本
├── stop.sh              # 停止脚本
├── LICENSE              # MIT许可证
└── README.md            # 本文件
```

### 技术栈

- **Python 3.11**: 主要编程语言
- **Paramiko**: SSH服务器实现
- **PyYAML**: 配置文件解析
- **Docker**: 容器化部署

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## ⚠️ 安全说明

1. **修改默认密码**: 生产环境请务必修改默认的SSH用户名和密码
2. **网络隔离**: 建议将代理服务部署在安全的网络区域
3. **日志审计**: 定期检查日志文件，监控异常访问
4. **最小权限**: 仅启用需要的端口映射
5. **更新维护**: 定期更新依赖包和Docker镜像

## 📞 支持

如有问题或建议，请提交Issue或联系维护者。

## 🙏 致谢

感谢所有为此项目做出贡献的开发者！

---

**注意**: Telnet是明文协议，请确保代理服务器到Telnet设备之间的网络是安全可信的。

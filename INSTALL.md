# 安装指南

本文档提供了详细的安装和部署说明。

## 目录

- [Docker部署（推荐）](#docker部署推荐)
- [系统服务部署](#系统服务部署)
- [本地开发部署](#本地开发部署)
- [生产环境建议](#生产环境建议)

## Docker部署（推荐）

### 前置要求

- Docker 20.10+
- Docker Compose 1.29+ (或 Docker Compose V2)

### 快速部署

1. **下载项目**
```bash
git clone <repository-url>
cd telnet-ssh-proxy
```

2. **配置映射**
```bash
# 编辑配置文件
vim config.yaml

# 或使用管理工具
python manage.py add 4001 192.168.1.100 23 --description "设备1"
```

3. **启动服务**
```bash
# 使用启动脚本
./start.sh

# 或使用make
make start

# 或直接使用docker-compose
docker-compose up -d --build
```

4. **验证部署**
```bash
# 查看状态
docker ps

# 健康检查
make health

# 查看日志
make logs
```

## 系统服务部署

在Linux系统上作为系统服务运行，开机自启动。

### 1. 准备项目目录

```bash
sudo mkdir -p /opt/telnet-ssh-proxy
sudo cp -r * /opt/telnet-ssh-proxy/
cd /opt/telnet-ssh-proxy
```

### 2. 配置服务

```bash
# 复制systemd服务文件
sudo cp telnet-ssh-proxy.service /etc/systemd/system/

# 重新加载systemd
sudo systemctl daemon-reload

# 启用服务（开机自启动）
sudo systemctl enable telnet-ssh-proxy

# 启动服务
sudo systemctl start telnet-ssh-proxy
```

### 3. 管理服务

```bash
# 查看状态
sudo systemctl status telnet-ssh-proxy

# 停止服务
sudo systemctl stop telnet-ssh-proxy

# 重启服务
sudo systemctl restart telnet-ssh-proxy

# 查看日志
sudo journalctl -u telnet-ssh-proxy -f
```

## 本地开发部署

用于开发和测试。

### 1. 安装Python环境

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置

```bash
cp config.example.yaml config.yaml
vim config.yaml
```

### 4. 运行

```bash
# 运行代理服务
python proxy_server.py

# 或使用make
make dev
```

## 生产环境建议

### 1. 安全配置

**修改默认密码**
```yaml
# config.yaml
ssh:
  username: "your_secure_username"
  password: "your_strong_password"
```

**限制访问IP**

编辑 `docker-compose.yml`，绑定到特定IP：
```yaml
ports:
  - "192.168.1.10:4001-4032:4001-4032"
```

### 2. 网络配置

**防火墙规则**
```bash
# 只允许特定IP访问
sudo ufw allow from 192.168.1.0/24 to any port 4001:4032
```

**使用反向代理**

如需更高级的访问控制，可以使用Nginx或HAProxy作为反向代理。

### 3. 监控配置

**配置日志收集**

将日志目录挂载到日志收集系统：
```yaml
# docker-compose.yml
volumes:
  - /var/log/telnet-ssh-proxy:/app/logs
```

**集成监控系统**

可以集成Prometheus、Grafana等监控系统监控服务状态。

### 4. 备份策略

**备份配置和密钥**
```bash
# 定期备份
tar -czf backup-$(date +%Y%m%d).tar.gz config.yaml data/
```

**自动备份脚本**
```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/backup/telnet-ssh-proxy"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/backup-$DATE.tar.gz \
    config.yaml \
    data/ \
    --exclude='data/*.log'

# 保留最近7天的备份
find $BACKUP_DIR -name "backup-*.tar.gz" -mtime +7 -delete
```

### 5. 资源限制

编辑 `docker-compose.yml` 设置资源限制：
```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 1G
    reservations:
      cpus: '0.5'
      memory: 256M
```

### 6. 高可用部署

对于关键业务，可以部署多个实例：

```bash
# 节点1
docker-compose -p proxy1 up -d

# 节点2（不同服务器）
docker-compose -p proxy2 up -d
```

使用负载均衡器（如HAProxy）在实例之间分配流量。

## 升级

### Docker部署升级

```bash
# 停止服务
docker-compose down

# 拉取最新代码
git pull

# 重新构建并启动
docker-compose up -d --build
```

### 保持配置

升级时，您的配置文件、数据和日志会保留：
- `config.yaml` - 配置文件
- `data/` - SSH密钥等数据
- `logs/` - 日志文件

## 卸载

### Docker部署

```bash
# 停止并删除容器
docker-compose down

# 删除镜像
docker rmi telnet-ssh-proxy:latest

# 删除项目文件
cd .. && rm -rf telnet-ssh-proxy
```

### 系统服务

```bash
# 停止并禁用服务
sudo systemctl stop telnet-ssh-proxy
sudo systemctl disable telnet-ssh-proxy

# 删除服务文件
sudo rm /etc/systemd/system/telnet-ssh-proxy.service
sudo systemctl daemon-reload

# 删除项目文件
sudo rm -rf /opt/telnet-ssh-proxy
```

## 故障排查

### 查看详细日志

```bash
# Docker日志
docker logs telnet-ssh-proxy -f

# 应用日志
tail -f logs/proxy.log
```

### 调试模式

修改 `config.yaml`:
```yaml
logging:
  level: "DEBUG"
```

### 测试连接

```bash
# 测试SSH连接
./test_connection.sh -h localhost -p 4001

# 测试Telnet后端
telnet 192.168.1.100 23
```

## 获取帮助

- 查看文档: [README.md](README.md)
- 快速开始: [QUICKSTART.md](QUICKSTART.md)
- 提交Issue: GitHub Issues

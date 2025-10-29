# 快速参考手册

## 常用命令速查

### 服务管理

```bash
# 启动服务
./start.sh
# 或
make start
# 或
docker-compose up -d

# 停止服务
./stop.sh
# 或
make stop
# 或
docker-compose down

# 重启服务
make restart
# 或
./stop.sh && ./start.sh

# 查看状态
make status
# 或
docker ps

# 查看日志
make logs
# 或
docker logs -f telnet-ssh-proxy
```

### 端口映射管理

```bash
# 列出所有映射
python manage.py list
# 或在容器中
docker exec telnet-ssh-proxy python manage.py list

# 添加映射
python manage.py add 4001 192.168.1.100 23 --description "设备1"

# 启用映射
python manage.py enable 4001

# 禁用映射
python manage.py disable 4001

# 查看详情
python manage.py show 4001

# 删除映射
python manage.py remove 4001
```

### 使用Make命令

```bash
# 添加映射（需要在容器运行时）
make add PORT=4001 HOST=192.168.1.100 TELNET_PORT=23 DESC="设备1"

# 启用
make enable PORT=4001

# 禁用
make disable PORT=4001

# 查看详情
make show PORT=4001

# 列出所有
make list
```

### 健康检查

```bash
# 执行健康检查
make health
# 或
docker exec telnet-ssh-proxy python health_check.py
# 或
python health_check.py

# 持续监控
python monitor.py --continuous --interval 30
```

### 连接测试

```bash
# SSH连接
ssh -p 4001 ritts@localhost
# 密码: ritts

# 使用测试脚本
./test_connection.sh -h localhost -p 4001

# 性能测试
./benchmark.sh -h localhost -p 4001 -c 10 -d 60
```

### 故障排查

```bash
# 运行诊断工具
./troubleshoot.sh

# 查看最近日志
docker logs telnet-ssh-proxy --tail 50

# 查看错误日志
docker logs telnet-ssh-proxy 2>&1 | grep -i error

# 进入容器
docker exec -it telnet-ssh-proxy /bin/bash

# 检查端口监听
netstat -tuln | grep 400
# 或
ss -tuln | grep 400
```

## 配置示例

### 基本配置

```yaml
# config.yaml
ssh:
  username: "ritts"
  password: "ritts"

mappings:
  4001:
    host: "192.168.1.100"
    port: 23
    enabled: true
    description: "交换机1"
```

### 安全配置

```yaml
ssh:
  username: "admin"
  password: "YourStrongPassword123!"
```

### 自定义Telnet端口

```yaml
mappings:
  4001:
    host: "192.168.1.100"
    port: 2023  # 非标准端口
    enabled: true
```

## Docker命令

```bash
# 构建镜像
docker-compose build

# 查看容器
docker ps -a

# 查看资源使用
docker stats telnet-ssh-proxy

# 导出日志
docker logs telnet-ssh-proxy > proxy.log 2>&1

# 备份数据
tar -czf backup.tar.gz config.yaml data/ logs/

# 清理容器
docker-compose down -v

# 清理镜像
docker rmi telnet-ssh-proxy:latest
```

## 系统服务命令

```bash
# 安装服务
sudo cp telnet-ssh-proxy.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable telnet-ssh-proxy

# 管理服务
sudo systemctl start telnet-ssh-proxy
sudo systemctl stop telnet-ssh-proxy
sudo systemctl restart telnet-ssh-proxy
sudo systemctl status telnet-ssh-proxy

# 查看日志
sudo journalctl -u telnet-ssh-proxy -f
```

## 网络配置

### 防火墙设置

```bash
# UFW
sudo ufw allow 4001:4032/tcp

# 限制来源IP
sudo ufw allow from 192.168.1.0/24 to any port 4001:4032

# iptables
sudo iptables -A INPUT -p tcp --dport 4001:4032 -j ACCEPT

# 限制来源IP
sudo iptables -A INPUT -p tcp -s 192.168.1.0/24 --dport 4001:4032 -j ACCEPT
```

### 端口检查

```bash
# 检查端口监听
netstat -tuln | grep 4001
ss -tuln | grep 4001
lsof -i :4001

# 测试端口连通性
telnet localhost 4001
nc -zv localhost 4001
```

## 日志相关

```bash
# 实时查看日志
tail -f logs/proxy.log

# 查看错误日志
grep -i error logs/proxy.log

# 按时间查看
grep "2025-10-29 10:" logs/proxy.log

# 统计连接数
grep "接受来自" logs/proxy.log | wc -l

# 统计成功认证
grep "认证成功" logs/proxy.log | wc -l
```

## 性能优化

### 资源限制

```yaml
# docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 1G
```

### 日志大小控制

```yaml
# config.yaml
logging:
  max_bytes: 10485760  # 10MB
  backup_count: 5      # 保留5个文件
```

## 常见问题解决

### 无法连接

```bash
# 1. 检查容器状态
docker ps

# 2. 检查端口
netstat -tuln | grep 4001

# 3. 查看日志
docker logs telnet-ssh-proxy --tail 50

# 4. 检查配置
docker exec telnet-ssh-proxy python manage.py show 4001

# 5. 测试后端
telnet 192.168.1.100 23
```

### 认证失败

```bash
# 检查配置文件中的用户名密码
grep -A 3 "^ssh:" config.yaml
```

### 服务崩溃

```bash
# 查看崩溃日志
docker logs telnet-ssh-proxy

# 重启服务
./stop.sh && ./start.sh

# 运行诊断
./troubleshoot.sh
```

## 备份恢复

### 备份

```bash
# 完整备份
tar -czf backup-$(date +%Y%m%d).tar.gz \
    config.yaml data/ --exclude='data/*.log'

# 仅配置
cp config.yaml config.yaml.backup
```

### 恢复

```bash
# 解压备份
tar -xzf backup-20251029.tar.gz

# 恢复配置
cp config.yaml.backup config.yaml

# 重启服务
./stop.sh && ./start.sh
```

## 更新升级

```bash
# 拉取更新
git pull

# 重新构建
docker-compose down
docker-compose up -d --build

# 检查版本
cat VERSION
```

## 环境变量

```bash
# 指定配置文件
export CONFIG_FILE=/path/to/config.yaml

# 设置时区
export TZ=Asia/Shanghai

# 设置日志级别
export LOG_LEVEL=DEBUG
```

## 快捷别名

添加到 `~/.bashrc` 或 `~/.zshrc`:

```bash
alias proxy-start='cd /path/to/telnet-ssh-proxy && ./start.sh'
alias proxy-stop='cd /path/to/telnet-ssh-proxy && ./stop.sh'
alias proxy-logs='docker logs -f telnet-ssh-proxy'
alias proxy-status='docker ps | grep telnet-ssh-proxy'
alias proxy-list='docker exec telnet-ssh-proxy python manage.py list'
alias proxy-health='docker exec telnet-ssh-proxy python health_check.py'
```

## 监控告警脚本

```bash
#!/bin/bash
# monitor.sh - 简单监控脚本

while true; do
    if ! docker exec telnet-ssh-proxy python health_check.py; then
        echo "告警: 服务异常!" | mail -s "Proxy Alert" admin@example.com
    fi
    sleep 300  # 5分钟检查一次
done
```

## 有用的一行命令

```bash
# 查看活跃连接数
docker exec telnet-ssh-proxy netstat -an | grep ESTABLISHED | wc -l

# 查看最近的错误
docker logs telnet-ssh-proxy 2>&1 | grep ERROR | tail -10

# 统计今天的连接数
docker logs telnet-ssh-proxy | grep "$(date +%Y-%m-%d)" | grep "接受来自" | wc -l

# 查看容器资源使用
docker stats telnet-ssh-proxy --no-stream

# 快速重启
docker restart telnet-ssh-proxy
```

## 获取帮助

```bash
# 查看主文档
cat README.md | less

# 查看快速开始
cat QUICKSTART.md

# 查看安装指南
cat INSTALL.md

# 查看架构设计
cat ARCHITECTURE.md

# 管理工具帮助
python manage.py --help

# 监控工具帮助
python monitor.py --help
```

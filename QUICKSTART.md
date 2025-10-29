# 快速开始指南

## 一、准备工作

### 1. 确认Docker环境

```bash
docker --version
docker-compose --version
```

如未安装，请先安装Docker和Docker Compose。

### 2. 获取项目

```bash
git clone <repository-url>
cd telnet-ssh-proxy
```

## 二、配置端口映射

### 方法1: 编辑配置文件（推荐）

编辑 `config.yaml`:

```yaml
mappings:
  4001:
    host: "192.168.1.100"  # 替换为您的Telnet设备IP
    port: 23               # Telnet端口（通常是23）
    enabled: true          # 设置为true启用
    description: "我的设备1"
```

### 方法2: 使用管理工具

```bash
# 添加映射
python manage.py add 4001 192.168.1.100 23 --description "我的设备1"

# 查看所有映射
python manage.py list
```

## 三、启动服务

```bash
# 一键启动
./start.sh

# 或手动启动
docker-compose up -d --build
```

## 四、测试连接

```bash
# 使用SSH客户端连接
ssh -p 4001 ritts@localhost

# 密码: ritts
```

成功后，您将连接到配置的Telnet设备！

## 五、常用命令

### 查看状态

```bash
# 查看容器状态
docker ps

# 查看日志
docker logs -f telnet-ssh-proxy
```

### 管理映射

```bash
# 列出所有映射
docker exec telnet-ssh-proxy python manage.py list

# 启用映射
docker exec telnet-ssh-proxy python manage.py enable 4001

# 禁用映射
docker exec telnet-ssh-proxy python manage.py disable 4001
```

### 健康检查

```bash
docker exec telnet-ssh-proxy python health_check.py
```

### 停止服务

```bash
./stop.sh
```

## 六、修改默认密码（重要！）

生产环境请务必修改默认密码：

1. 编辑 `config.yaml`:
```yaml
ssh:
  username: "your_username"
  password: "your_strong_password"
```

2. 重启服务:
```bash
./stop.sh
./start.sh
```

## 七、故障排查

### 无法连接？

1. 检查端口是否启用:
```bash
docker exec telnet-ssh-proxy python manage.py show 4001
```

2. 检查Telnet后端是否可达:
```bash
telnet 192.168.1.100 23
```

3. 查看日志:
```bash
docker logs telnet-ssh-proxy | tail -50
```

## 需要帮助？

查看完整文档: [README.md](README.md)

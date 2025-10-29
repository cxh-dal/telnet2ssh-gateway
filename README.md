# Telnet → SSH 代理服务 (tts-proxy)

将不安全的 Telnet 会话通过安全的 SSH 通道暴露给用户：用户以 SSH 客户端连接到本服务，对应端口一对一映射到后端 Telnet 设备，流量在用户侧为加密的 SSH，服务端与设备间为 Telnet。

- **实时双向透明转发**：逐字节全双工，支持控制字符与原始字节。
- **高并发稳定**：多端口监听，多用户并发。
- **端口映射**：默认监听 `4001-4032` 共 32 个端口；每个端口对应一个 Telnet 目标地址。
- **Docker 一键部署**：内置镜像与 `docker-compose.yml`。
- **便捷 CLI**：容器内置 `tts-proxy` 命令，管理端口映射。
- **健康检查与监控**：HTTP `/healthz` 与 `/metrics`（JSON）。
- **默认 SSH 凭据**：用户名与密码均为 `ritts`（可通过环境变量覆盖）。
- **开源协议**：Apache-2.0（可商用）。

## 工作原理

1. 服务在多个 SSH 端口上监听（默认 `4001-4032`）。
2. 用户使用 SSH 客户端连接某端口（例如 `-p 4001`），完成密码认证。
3. 服务查找该端口映射的 Telnet 目标 `host:port`，与设备建立 TCP 连接。
4. 建立逐字节双向转发通道（包含最小化的 Telnet 协议协商处理），实现透明交互。

> 说明：服务作为“最简 Telnet 客户端”对基础协商（WILL/DO/DONT/WONT/SB）做了中立响应与过滤，绝大多数网络设备可正常交互。

## 快速开始（Docker Compose）

```bash
# 1) 启动
docker compose up -d

# 2) 设置端口映射（示例：将 4001 映射到 10.0.0.5:23）
docker exec -it tts-proxy tts-proxy map set 4001 10.0.0.5:23

# 3) 查看映射
docker exec -it tts-proxy tts-proxy map list

# 4) 连接测试（本机）
ssh -p 4001 ritts@127.0.0.1   # 密码：ritts
```

默认会创建数据目录 `./data`，用于存放配置与 SSH 主机密钥。

## 配置项与环境变量

- `CONFIG_PATH`：配置文件路径（默认 `/data/config.json`）。
- `HOST_KEY_PATH`：SSH 主机私钥（RSA）路径（默认 `/data/ssh_host_rsa_key`，自动生成）。
- `HEALTH_ADDR`：健康检查 HTTP 监听地址（默认 `:8080`）。
- `SSH_USERNAME` / `SSH_PASSWORD`：SSH 登录凭据（默认均为 `ritts`）。

配置文件 JSON 结构（默认会自动创建）：

```json
{
  "listen_ports": [],
  "mappings": {
    "4001": "10.0.0.5:23",
    "4002": "192.168.1.33:2323"
  }
}
```

- `listen_ports` 为空则默认监听 `4001-4032`。
- `mappings` 管理端口与 Telnet 目标的一对一映射。

## CLI 用法（容器内）

```bash
# 列表
tts-proxy map list

# 设置映射
tts-proxy map set <port> <host:port>
# 例：tts-proxy map set 4001 10.0.0.5:23

# 删除映射
tts-proxy map delete <port>

# 连通性测试
tts-proxy test <port>
```

服务启动：

```bash
tts-proxy serve
```

> 小贴士：使用 `docker exec -it tts-proxy ...` 在容器内执行上述命令；或以 `docker run --rm -v $(pwd)/data:/data <image> tts-proxy map ...` 的方式离线管理映射文件。

## 健康检查与监控

- `GET /healthz`：返回 JSON 状态（监听端口数量、活动会话数、累计会话数、上/下行字节数）。
- `GET /metrics`：返回基础指标（JSON 格式）。

在 `docker-compose.yml` 中默认映射 `8080:8080` 可供外部探活与观测（建议配合容器编排的 `restart: always`）。

## 安全与账号

- 默认 SSH 用户名/密码为 `ritts/ritts`，请在生产环境通过环境变量覆盖。
- 建议仅在受控网络中暴露代理端口，并通过防火墙/安全组限制访问源。
- SSH 主机密钥会在首次启动时自动生成并持久化在 `/data` 下。

## 端口与并发

- 默认监听 `4001-4032` 共 32 个端口，可同时为多个用户与多个后端设备提供会话。
- 每个端口是一对一映射到某个 Telnet 目标；多个用户可同时连接同一端口（独立会话）。

## 构建

```bash
# 本地构建二进制
GOOS=linux GOARCH=amd64 CGO_ENABLED=0 go build -o bin/tts-proxy ./cmd/tts-proxy

# Docker 镜像
docker build -t tts-proxy:latest .
```

## 开源许可

本项目采用 Apache-2.0 许可证，详见 `LICENSE` 文件，可自由用于商业与非商业用途。

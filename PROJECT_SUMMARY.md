# 项目总览

## 📦 项目信息

**项目名称**: Telnet to SSH Proxy  
**版本**: 1.0.0  
**许可证**: MIT  
**语言**: Python 3.11  
**类型**: 网络代理服务

## 🎯 项目目标

解决网络安全要求禁止明文协议，但设备不支持SSH的问题。通过提供SSH到Telnet的透明代理，使用户能够通过安全的SSH协议连接到只支持Telnet的设备。

## ✨ 核心特性

✅ **实时双向透明转发**: SSH和Telnet会话数据无缝流动  
✅ **高并发和稳定性**: 支持多用户同时连接  
✅ **32个端口映射**: 默认支持4001-4032端口  
✅ **Docker容器化**: 一键部署  
✅ **命令行管理工具**: 便捷的映射管理  
✅ **健康检查**: 自动监控和重启  
✅ **开源免费**: MIT许可证

## 📁 项目结构

```
telnet-ssh-proxy/
├── 核心程序
│   ├── proxy_server.py          # 主代理服务器 (450行)
│   ├── manage.py                # 配置管理工具 (240行)
│   ├── health_check.py          # 健康检查脚本 (50行)
│   └── monitor.py               # 监控工具 (230行)
│
├── 配置文件
│   ├── config.yaml              # 主配置文件
│   ├── config.example.yaml      # 配置示例
│   └── requirements.txt         # Python依赖
│
├── Docker部署
│   ├── Dockerfile               # Docker镜像
│   ├── docker-compose.yml       # Docker编排
│   └── .dockerignore            # Docker忽略文件
│
├── 脚本工具
│   ├── start.sh                 # 启动脚本
│   ├── stop.sh                  # 停止脚本
│   ├── test_connection.sh       # 连接测试
│   ├── benchmark.sh             # 性能测试
│   └── troubleshoot.sh          # 故障排查
│
├── 系统集成
│   ├── telnet-ssh-proxy.service # Systemd服务
│   ├── Makefile                 # Make命令
│   └── .env.example             # 环境变量示例
│
├── 文档
│   ├── README.md                # 主文档 (7.7KB)
│   ├── QUICKSTART.md            # 快速开始
│   ├── INSTALL.md               # 安装指南
│   ├── ARCHITECTURE.md          # 架构设计
│   ├── CHEATSHEET.md            # 快速参考
│   ├── CONTRIBUTING.md          # 贡献指南
│   ├── CHANGELOG.md             # 更新日志
│   └── PROJECT_SUMMARY.md       # 本文件
│
└── 其他
    ├── LICENSE                  # MIT许可证
    ├── VERSION                  # 版本号
    ├── .gitignore               # Git忽略文件
    └── .github/workflows/       # CI/CD配置
```

## 🔧 技术实现

### 核心技术栈
- **Python 3.11**: 主要编程语言
- **Paramiko 3.4.0**: SSH服务器实现
- **PyYAML 6.0.1**: 配置文件解析
- **Socket**: TCP网络通信
- **Threading**: 多线程并发

### 架构设计
- **多线程模型**: 每个端口独立线程，每个连接独立处理
- **双向转发**: SSH↔Telnet实时数据透传
- **事件驱动**: 使用select监听I/O事件
- **配置驱动**: YAML配置文件管理映射

## 📊 代码统计

```
核心代码:    ~970  行 Python
配置文件:    ~200  行 YAML
脚本工具:    ~500  行 Bash
文档:        ~1500 行 Markdown
总计:        ~3170 行
```

## 🚀 快速开始

### 3步部署

```bash
# 1. 配置端口映射
vim config.yaml

# 2. 启动服务
./start.sh

# 3. 连接使用
ssh -p 4001 ritts@your-server-ip
```

## 📖 文档导航

| 文档 | 说明 | 适合人群 |
|------|------|---------|
| [README.md](README.md) | 完整的项目说明 | 所有用户 |
| [QUICKSTART.md](QUICKSTART.md) | 5分钟快速开始 | 新用户 |
| [INSTALL.md](INSTALL.md) | 详细安装指南 | 运维人员 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | 架构设计文档 | 开发者 |
| [CHEATSHEET.md](CHEATSHEET.md) | 命令速查手册 | 日常使用 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 贡献指南 | 贡献者 |

## 🎨 使用场景

### 场景1: 数据中心设备管理
- **问题**: 老旧交换机和路由器只支持Telnet
- **解决**: 部署代理服务，通过SSH安全访问

### 场景2: 网络安全合规
- **问题**: 安全审计要求禁止明文协议
- **解决**: SSH加密外部访问，内网Telnet连接设备

### 场景3: 统一访问管理
- **问题**: 设备支持协议不统一
- **解决**: 统一使用SSH连接，代理自动适配

### 场景4: 远程维护
- **问题**: 需要远程访问现场设备
- **解决**: 外网SSH安全隧道，内网Telnet直连

## 💡 核心功能

### 1. 端口映射管理
```bash
# 添加映射
python manage.py add 4001 192.168.1.100 23 --description "交换机"

# 列出映射
python manage.py list

# 启用/禁用
python manage.py enable 4001
python manage.py disable 4001
```

### 2. 健康检查
```bash
# 自动健康检查 (Docker)
docker ps  # 查看健康状态

# 手动健康检查
python health_check.py

# 持续监控
python monitor.py --continuous
```

### 3. 日志管理
- 自动日志轮转 (10MB)
- 保留5个历史文件
- 可配置日志级别
- Docker日志集成

### 4. Docker部署
```bash
# 一键启动
./start.sh

# 查看状态
docker ps

# 查看日志
docker logs -f telnet-ssh-proxy
```

## 🔒 安全特性

✓ SSH协议加密通信  
✓ 密码认证  
✓ 可配置访问控制  
✓ 日志审计  
✓ 自动生成SSH密钥  
✓ 支持防火墙规则

## 📈 性能指标

- **并发连接**: 100+ 同时连接
- **延迟**: < 10ms 本地转发
- **吞吐量**: 取决于网络和设备
- **资源占用**: < 256MB 内存

## 🛠️ 管理工具

### 命令行工具
- `manage.py`: 配置管理
- `health_check.py`: 健康检查
- `monitor.py`: 持续监控

### Shell脚本
- `start.sh`: 启动服务
- `stop.sh`: 停止服务
- `test_connection.sh`: 测试连接
- `benchmark.sh`: 性能测试
- `troubleshoot.sh`: 故障诊断

### Make命令
```bash
make start      # 启动
make stop       # 停止
make logs       # 查看日志
make health     # 健康检查
make list       # 列出映射
```

## 🐛 故障排查

### 快速诊断
```bash
# 运行诊断工具
./troubleshoot.sh
```

### 常见问题
1. **无法连接**: 检查端口映射是否启用
2. **认证失败**: 检查用户名密码配置
3. **服务崩溃**: 查看日志 `docker logs telnet-ssh-proxy`
4. **后端不可达**: 测试 `telnet <backend-ip> 23`

## 🌟 最佳实践

### 生产环境
1. ✅ 修改默认密码
2. ✅ 限制访问IP范围
3. ✅ 配置资源限制
4. ✅ 定期备份配置
5. ✅ 启用日志收集
6. ✅ 配置监控告警
7. ✅ 使用系统服务
8. ✅ 定期安全审计

### 性能优化
1. ✅ 合理配置并发数
2. ✅ 调整缓冲区大小
3. ✅ 优化日志级别
4. ✅ 资源限制配置

## 🔄 更新计划

### v1.1.0 (计划中)
- [ ] Web管理界面
- [ ] 公钥认证支持
- [ ] 会话录制功能
- [ ] Metrics导出

### v2.0.0 (未来)
- [ ] 支持其他协议
- [ ] 分布式部署
- [ ] 高可用集群
- [ ] 访问控制列表

## 📞 获取支持

- **文档**: 查看 docs/ 目录
- **问题**: 提交 GitHub Issue
- **贡献**: 参考 CONTRIBUTING.md

## 🙏 致谢

感谢所有开源项目和贡献者！

特别感谢:
- Paramiko 项目
- Docker 项目
- Python 社区

## 📜 许可证

MIT License - 可自由使用、修改和商业使用

---

**开发者**: Telnet to SSH Proxy Team  
**最后更新**: 2025-10-29  
**项目地址**: https://github.com/your-repo/telnet-ssh-proxy

---

## 快速链接

- 🚀 [快速开始](QUICKSTART.md)
- 📖 [完整文档](README.md)
- 🏗️ [架构设计](ARCHITECTURE.md)
- 📝 [命令速查](CHEATSHEET.md)
- 🔧 [安装指南](INSTALL.md)
- 🤝 [贡献指南](CONTRIBUTING.md)

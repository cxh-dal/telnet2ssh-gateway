# 更新日志

所有重要的项目更改都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [1.0.0] - 2025-10-29

### 新增
- 🎉 初始版本发布
- ✨ SSH到Telnet的透明代理功能
- 🔄 实时双向数据转发
- 🚀 支持32个端口映射（4001-4032）
- 🛠️ 命令行管理工具
- 🐳 Docker容器化部署
- 💚 健康检查和自动重启
- 📊 日志记录和轮转
- 📖 完整的文档
- 🔒 MIT开源许可

### 功能特性
- 支持所有SSH客户端
- 支持PTY和原始数据传输
- 支持控制字符透传
- 高并发连接支持
- 配置文件管理
- 端口映射的启用/禁用
- 健康检查端点
- Docker日志集成
- 自动生成SSH主机密钥

### 文档
- README.md - 主要文档
- QUICKSTART.md - 快速开始指南
- INSTALL.md - 详细安装指南
- CONTRIBUTING.md - 贡献指南

### 工具
- manage.py - 端口映射管理工具
- health_check.py - 健康检查脚本
- start.sh / stop.sh - 启停脚本
- test_connection.sh - 连接测试脚本
- Makefile - 便捷命令

[1.0.0]: https://github.com/your-repo/telnet-ssh-proxy/releases/tag/v1.0.0

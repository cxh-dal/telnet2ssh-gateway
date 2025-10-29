# 贡献指南

感谢您对 Telnet to SSH Proxy 项目的关注！我们欢迎各种形式的贡献。

## 如何贡献

### 报告Bug

如果您发现了Bug，请通过GitHub Issues报告，并包含以下信息：

- 详细的问题描述
- 复现步骤
- 预期行为
- 实际行为
- 环境信息（操作系统、Docker版本等）
- 相关日志

### 提出新功能

如果您有好的想法，欢迎提交Feature Request，包含：

- 功能描述
- 使用场景
- 预期效果

### 提交代码

1. **Fork项目**
```bash
# 在GitHub上Fork项目
# 克隆您的Fork
git clone https://github.com/your-username/telnet-ssh-proxy.git
cd telnet-ssh-proxy
```

2. **创建分支**
```bash
git checkout -b feature/your-feature-name
```

3. **进行开发**
- 遵循现有代码风格
- 添加必要的注释
- 更新相关文档

4. **测试**
```bash
# 运行测试
python proxy_server.py

# 测试连接
./test_connection.sh
```

5. **提交更改**
```bash
git add .
git commit -m "Add: 您的功能描述"
```

提交信息格式：
- `Add: 新增功能`
- `Fix: 修复问题`
- `Update: 更新功能`
- `Docs: 文档更新`
- `Refactor: 代码重构`

6. **推送并创建PR**
```bash
git push origin feature/your-feature-name
```

然后在GitHub上创建Pull Request。

## 代码规范

### Python代码

- 遵循PEP 8规范
- 使用有意义的变量名
- 添加文档字符串
- 保持函数简洁

示例：
```python
def connect_to_telnet(host: str, port: int, timeout: int = 10) -> bool:
    """
    连接到Telnet服务器
    
    Args:
        host: Telnet服务器地址
        port: Telnet服务器端口
        timeout: 连接超时时间（秒）
    
    Returns:
        bool: 连接是否成功
    """
    # 实现代码
    pass
```

### 文档

- 使用清晰的中文描述
- 提供代码示例
- 保持格式一致

## 开发环境设置

### 1. 安装依赖

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 配置开发环境

```bash
cp config.example.yaml config.yaml
# 根据需要修改配置
```

### 3. 运行测试

```bash
python proxy_server.py
```

## 发布流程

维护者发布新版本的流程：

1. 更新版本号
```bash
echo "1.1.0" > VERSION
```

2. 更新CHANGELOG
```bash
# 编辑 CHANGELOG.md
```

3. 提交更改
```bash
git add VERSION CHANGELOG.md
git commit -m "Release: v1.1.0"
git tag v1.1.0
```

4. 推送
```bash
git push origin main
git push origin v1.1.0
```

## 行为准则

- 尊重他人
- 建设性沟通
- 欢迎新人
- 专注于技术讨论

## 许可证

通过贡献代码，您同意您的贡献将在MIT许可证下发布。

## 联系方式

如有问题，可以通过以下方式联系：

- GitHub Issues
- Pull Request讨论

再次感谢您的贡献！🎉

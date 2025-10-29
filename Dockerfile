FROM python:3.11-slim

LABEL maintainer="Telnet to SSH Proxy"
LABEL description="将SSH连接代理到Telnet后端设备"

# 设置工作目录
WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用文件
COPY proxy_server.py .
COPY manage.py .
COPY health_check.py .
COPY config.yaml .

# 创建数据和日志目录
RUN mkdir -p /app/data /app/logs

# 设置环境变量
ENV CONFIG_FILE=/app/config.yaml
ENV PYTHONUNBUFFERED=1

# 暴露端口范围 4001-4032
EXPOSE 4001-4032

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python health_check.py || exit 1

# 设置启动命令
CMD ["python", "proxy_server.py"]

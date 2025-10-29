.PHONY: help build start stop restart logs status clean health list

help: ## 显示帮助信息
	@echo "Telnet to SSH Proxy - 可用命令:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""

build: ## 构建Docker镜像
	docker-compose build

start: ## 启动服务
	@echo "启动 Telnet to SSH Proxy 服务..."
	@mkdir -p data logs
	docker-compose up -d
	@echo "服务已启动！"
	@make status

stop: ## 停止服务
	@echo "停止服务..."
	docker-compose down
	@echo "服务已停止"

restart: stop start ## 重启服务

logs: ## 查看日志
	docker-compose logs -f

status: ## 查看服务状态
	@echo "服务状态:"
	@docker-compose ps

health: ## 健康检查
	@echo "执行健康检查..."
	@docker exec telnet-ssh-proxy python health_check.py || echo "健康检查失败"

list: ## 列出端口映射
	@docker exec telnet-ssh-proxy python manage.py list

clean: ## 清理容器和镜像
	docker-compose down -v
	docker rmi telnet-ssh-proxy:latest || true

install: ## 安装Python依赖（本地开发）
	pip install -r requirements.txt

dev: ## 本地开发模式运行
	python proxy_server.py

# 管理命令
add: ## 添加端口映射 (使用: make add PORT=4001 HOST=192.168.1.100 TELNET_PORT=23 DESC="设备1")
	@docker exec telnet-ssh-proxy python manage.py add $(PORT) $(HOST) $(TELNET_PORT) --description "$(DESC)"

enable: ## 启用端口映射 (使用: make enable PORT=4001)
	@docker exec telnet-ssh-proxy python manage.py enable $(PORT)

disable: ## 禁用端口映射 (使用: make disable PORT=4001)
	@docker exec telnet-ssh-proxy python manage.py disable $(PORT)

show: ## 显示端口详情 (使用: make show PORT=4001)
	@docker exec telnet-ssh-proxy python manage.py show $(PORT)

remove: ## 删除端口映射 (使用: make remove PORT=4001)
	@docker exec telnet-ssh-proxy python manage.py remove $(PORT)

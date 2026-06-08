#!/bin/bash
# 食光应用启动脚本（全栈 docker-compose：backend + frontend）

set -e

PROJECT_DIR="/vol1/1000/meal-planner"
cd "$PROJECT_DIR"

echo "🍽️ 启动食光应用..."

# 关掉可能残留的裸 uvicorn（老版 bare-metal 后端），避免占用 8000 端口
pkill -f "uvicorn app.main:app" || true

# 前端静态产物：若缺失且本机有 npm，则构建
if [ ! -d "frontend/dist" ]; then
    if command -v npm >/dev/null 2>&1; then
        echo "📦 构建前端产物..."
        (cd frontend && npm install && npm run build)
    else
        echo "⚠️  frontend/dist 不存在且未找到 npm；请先在有 Node 的机器上执行 npm run build"
    fi
fi

# 构建并启动 backend + frontend 容器
echo "🚀 构建并启动容器..."
docker-compose up -d --build

IP=$(hostname -I | awk '{print $1}')
echo "✅ 启动完成！"
echo "前端访问地址: http://$IP:7878"
echo "后端API地址: http://$IP:8000"
echo "API文档: http://$IP:8000/docs"

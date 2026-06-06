#!/bin/bash
# 食光应用启动脚本

set -e

PROJECT_DIR="/vol1/1000/meal-planner"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

echo "🍽️ 启动食光应用..."

# 检查并安装Python依赖
echo "📦 检查Python依赖..."
cd "$BACKEND_DIR"
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ -q
pip install pydantic-settings -i https://mirrors.aliyun.com/pypi/simple/ -q

# 启动后端
echo "🚀 启动后端服务..."
pkill -f "uvicorn app.main:app" || true
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > "$PROJECT_DIR/backend.log" 2>&1 &
echo "后端PID: $!"

# 启动前端（nginx容器）
echo "🌐 启动前端服务..."
cd "$PROJECT_DIR"
docker-compose up -d frontend

echo "✅ 启动完成！"
echo "前端访问地址: http://$(hostname -I | awk '{print $1}'):7878"
echo "后端API地址: http://$(hostname -I | awk '{print $1}'):8000"
echo "API文档: http://$(hostname -I | awk '{print $1}'):8000/docs"

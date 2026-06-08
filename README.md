# 食光 🍽️

一款温馨的家庭每日菜单推荐与食谱管理应用，解决"今天吃什么"的日常烦恼。

## ✨ 功能特性

- **智能推荐** — 根据历史记录和口味偏好，智能推荐每日菜品
- **心情推荐** — 选择当前心情，获得匹配的菜品推荐
- **转盘抽奖** — 美食转盘随机选菜，告别选择困难
- **盲盒惊喜** — 翻牌揭晓今日惊喜菜品
- **周计划** — 一键生成本周菜单，自动生成购物清单
- **用餐记录** — 记录每餐，评分与备注，美食照片墙
- **成就系统** — 80+成就自动解锁，培养烹饪习惯

## 🛠️ 技术栈

### 前端
- Vue 3 + TypeScript
- Vite
- Naive UI
- Pinia
- Vue Router 4
- ECharts

### 后端
- Python 3.11+
- FastAPI
- SQLAlchemy 2.0
- SQLite
- Pydantic v2

### 部署
- Docker + docker-compose
- Nginx

## 🚀 快速开始

### 方式一：Docker部署（推荐，全栈）

```bash
# 克隆项目
git clone <repository-url>
cd meal-planner

# 构建并启动 backend + frontend（首次或代码更新后加 --build）
docker-compose up -d --build

# 访问应用
# 前端：http://localhost:7878
# 后端API：http://localhost:8000
# API文档：http://localhost:8000/docs
```

> 前端容器内的 nginx 通过 compose 网络以服务名 `backend:8000` 反代 API，无需硬编码宿主机 IP。
> 前端走静态产物 `frontend/dist`，若尚未构建请先 `cd frontend && npm install && npm run build`。
> 首次启动后接入数据库迁移链：`docker-compose exec backend alembic stamp head`（详见「数据库迁移」）。

### 方式二：本地开发

#### 后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 启动后端
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 📁 项目结构

```
meal-planner/
├── frontend/                # 前端项目
│   ├── src/
│   │   ├── api/             # API请求封装
│   │   ├── components/      # 公共组件
│   │   ├── views/           # 页面组件
│   │   ├── stores/          # Pinia状态管理
│   │   ├── router/          # 路由配置
│   │   ├── utils/           # 工具函数
│   │   └── assets/          # 静态资源
│   ├── public/
│   ├── index.html
│   ├── vite.config.ts
│   └── package.json
├── backend/                 # 后端项目
│   ├── app/
│   │   ├── api/             # API路由
│   │   ├── models/          # 数据模型
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # 业务逻辑
│   │   ├── core/            # 核心配置
│   │   └── main.py          # 入口文件
│   ├── data/                # SQLite数据库
│   ├── uploads/             # 上传的图片
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
├── nginx.conf
├── PLAN.md                  # 开发规划
└── README.md
```

## 📝 API文档

启动后端后访问：http://localhost:8000/docs

### 主要API

- `GET /api/dishes` — 获取菜品列表
- `POST /api/dishes` — 创建菜品
- `GET /api/dishes/{id}` — 获取菜品详情
- `PUT /api/dishes/{id}` — 更新菜品
- `DELETE /api/dishes/{id}` — 删除菜品
- `GET /api/recommend/daily` — 每日推荐
- `GET /api/recommend/mood` — 心情推荐
- `GET /api/recommend/random` — 随机推荐
- `GET /api/records` — 获取用餐记录
- `POST /api/records` — 创建用餐记录
- `GET /api/stats/dashboard` — 仪表盘数据

## 🗄️ 数据库迁移（Alembic）

数据库结构变更通过 Alembic 管理。**不要再依赖应用启动时的 `create_all` 给已有表加列**——它只新建不存在的表，不会 `ALTER` 已存在的表，否则升级后会“丢列”（如曾经的 `pantry_items.expires_at`）。

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 新库接入迁移链：首次启动 create_all 建好表后，把当前结构标记为基线
alembic stamp head

# 改了 models 之后：生成并应用迁移
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

Docker 部署时在容器内执行：

```bash
docker-compose exec backend alembic upgrade head
```

> 已部署且结构漂移的旧库（例如缺 `expires_at`）：先 `alembic stamp head` 接入，再
> `alembic revision --autogenerate -m "reconcile"` 让 Alembic 对比 models 补出缺失列，最后 `alembic upgrade head`。

## 🎨 视觉风格

简约现代风格，温馨舒适，响应式设计支持移动端。

## 📦 成就系统

### 用餐类
- 初入厨房：记录第一餐
- 连续7天：连续7天记录用餐
- 连续30天：连续30天记录用餐
- 百菜斩：记录100道不同菜品
- 美食家：记录500道菜品

### 心情类
- 心情达人：使用5种不同心情
- 全心情解锁：使用所有心情推荐

### 推荐类
- 转盘达人：使用转盘50次
- 盲盒收藏家：使用盲盒30次

### 收藏类
- 收藏家：收藏20道菜品
- 美食家：收藏50道菜品

### 记录类
- 记录达人：记录50餐
- 美食摄影师：上传20张照片

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

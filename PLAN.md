# 食光 - 开发规划

## 项目概述

一款温馨的家庭每日菜单推荐与食谱管理应用，解决"今天吃什么"的日常烦恼。

### 目标用户
- 情侣/小家庭
- 想要规律饮食但懒得每天想菜谱的人

### 核心价值
- 智能推荐，告别选择困难
- 记录美食生活，培养烹饪习惯
- 自动生成购物清单，省时省力

---

## 已确认事项

- **应用名称**: 食光
- **视觉风格**: 简约现代
- **用户模式**: 单用户
- **PWA支持**: 否（纯Web应用）

---

## 功能模块

### 1. 菜品管理（核心）
- 菜品CRUD（名称、图片、分类、口味、难度）
- 食材与调料管理
- 烹饪步骤（支持计时）
- 菜品启用/禁用/收藏

### 2. 智能推荐
- **午/晚餐推荐** — 根据分类、口味、历史记录智能推荐
- **心情推荐** — 选择心情（开心/疲惫/想偷懒/想吃辣/想养生）匹配菜品
- **转盘抽奖** — 美食转盘随机选菜
- **盲盒惊喜** — 翻牌揭晓今日惊喜菜品
- **收藏加权** — 收藏的菜品推荐权重更高

### 3. 周计划
- 一键生成本周午/晚餐菜单
- 支持手动调整、换菜
- 购物清单自动汇总（按蔬菜/肉类/配料分类）

### 4. 记录与回顾
- 用餐记录（吃了什么、评分、备注）
- 照片墙（时间线展示美食照片）
- 历史回顾

### 5. 成就系统
- 自动解锁成就（初入厨房、连续七天、百菜斩等）
- 按维度分类（用餐/心情/推荐/照片/收藏）

### 6. 管理后台
- 仪表盘（菜品数、记录数、分类分布、热门菜品）
- 系统设置（重复天数、每日菜品数、分类、口味）

---

## 技术选型

### 前端
- **框架**: Vue 3 + TypeScript
- **构建工具**: Vite
- **UI组件库**: Naive UI（轻量、好看、Vue3原生支持）
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **HTTP客户端**: Axios
- **图表**: ECharts（统计面板用）
- **动画**: VueUse + CSS动画（转盘、盲盒用）

### 后端
- **语言**: Python 3.11+
- **框架**: FastAPI（高性能、自动文档）
- **数据库**: SQLite（单文件，无需额外服务）
- **ORM**: SQLAlchemy 2.0
- **数据验证**: Pydantic v2
- **图片处理**: Pillow
- **文件存储**: 本地文件系统

### 部署
- **容器化**: Docker + docker-compose
- **反向代理**: Nginx（可选，处理静态文件和HTTPS）
- **数据持久化**: Docker Volume挂载

---

## 数据库设计

### 核心表

#### dishes（菜品表）
```sql
CREATE TABLE dishes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,                    -- 菜品名称
    category TEXT NOT NULL,                -- 分类（荤菜/素菜/汤/主食/凉菜/小吃）
    taste TEXT,                            -- 口味（清淡/微辣/中辣/重辣/酸甜/咸鲜/麻辣/酸辣/五香/蒜香）
    difficulty INTEGER DEFAULT 1,          -- 难度（1-5）
    cook_time INTEGER,                     -- 烹饪时间（分钟）
    is_enabled BOOLEAN DEFAULT TRUE,       -- 是否启用
    is_favorite BOOLEAN DEFAULT FALSE,     -- 是否收藏
    image_url TEXT,                        -- 主图路径
    video_url TEXT,                        -- 视频路径（可选）
    description TEXT,                      -- 简介
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### ingredients（食材表）
```sql
CREATE TABLE ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dish_id INTEGER NOT NULL,
    name TEXT NOT NULL,                    -- 食材名称
    amount TEXT,                           -- 用量（如"200g"）
    type TEXT,                             -- 类型（主料/调料）
    FOREIGN KEY (dish_id) REFERENCES dishes(id) ON DELETE CASCADE
);
```

#### steps（烹饪步骤表）
```sql
CREATE TABLE steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dish_id INTEGER NOT NULL,
    step_number INTEGER NOT NULL,          -- 步骤序号
    description TEXT NOT NULL,             -- 步骤描述
    duration INTEGER,                      -- 计时（秒）
    FOREIGN KEY (dish_id) REFERENCES dishes(id) ON DELETE CASCADE
);
```

#### meal_records（用餐记录表）
```sql
CREATE TABLE meal_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dish_id INTEGER NOT NULL,
    meal_type TEXT NOT NULL,               -- 午餐/晚餐
    rating INTEGER,                        -- 评分（1-5）
    note TEXT,                             -- 备注
    photo_url TEXT,                        -- 照片路径
    record_date DATE NOT NULL,             -- 记录日期
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dish_id) REFERENCES dishes(id)
);
```

#### weekly_plans（周计划表）
```sql
CREATE TABLE weekly_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    week_start DATE NOT NULL,              -- 周开始日期
    day_of_week INTEGER NOT NULL,          -- 星期几（1-7）
    meal_type TEXT NOT NULL,               -- 午餐/晚餐
    dish_id INTEGER NOT NULL,
    FOREIGN KEY (dish_id) REFERENCES dishes(id)
);
```

#### achievements（成就表）
```sql
CREATE TABLE achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,                    -- 成就名称
    description TEXT,                      -- 成就描述
    icon TEXT,                             -- 图标
    category TEXT,                         -- 分类（用餐/心情/推荐等）
    condition_type TEXT,                   -- 条件类型
    condition_value INTEGER,               -- 条件值
    is_unlocked BOOLEAN DEFAULT FALSE,
    unlocked_at TIMESTAMP
);
```

---

## 成就系统设计

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

---

## API设计

### 菜品相关
```
GET    /api/dishes              -- 获取菜品列表（支持筛选、分页）
GET    /api/dishes/{id}         -- 获取菜品详情
POST   /api/dishes              -- 新增菜品
PUT    /api/dishes/{id}         -- 更新菜品
DELETE /api/dishes/{id}         -- 删除菜品
POST   /api/dishes/{id}/image   -- 上传菜品图片
```

### 推荐相关
```
GET    /api/recommend/daily     -- 每日推荐（午/晚餐）
GET    /api/recommend/mood      -- 心情推荐
GET    /api/recommend/random    -- 随机推荐（转盘用）
```

### 周计划相关
```
GET    /api/weekly-plan         -- 获取本周计划
POST   /api/weekly-plan/generate -- 自动生成本周计划
PUT    /api/weekly-plan/{id}    -- 修改计划项
GET    /api/shopping-list       -- 获取购物清单
```

### 记录相关
```
GET    /api/records             -- 获取用餐记录
POST   /api/records             -- 新增记录
GET    /api/records/timeline    -- 获取时间线（照片墙用）
```

### 成就相关
```
GET    /api/achievements        -- 获取所有成就
GET    /api/achievements/unlocked -- 获取已解锁成就
```

### 统计相关
```
GET    /api/stats/dashboard     -- 仪表盘数据
GET    /api/stats/trend         -- 趋势数据
```

---

## 项目结构

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
├── nginx.conf               # Nginx配置（可选）
├── PLAN.md                  # 本文件
└── README.md
```

---

## 开发计划

> **当前状态盘点 · 2026-06-07**
> 图例：✅ 已完成 · 🚧 部分完成（详见备注）· ❌ 未开始

### Phase 1：基础框架（1-2天）— ✅ 100%
- ✅ 搭建 Vue3 + Vite 前端项目
- ✅ 搭建 FastAPI 后端项目
- ✅ 数据库初始化脚本（`backend/init_data.py` 含 48 道预置菜品）
- ✅ 基础 CRUD API（菜品）
- ✅ 前后端联调（vite proxy + nginx 反代）

### Phase 2：核心功能（3-5天）— 🚧 70%
- ✅ 菜品列表 / 新增 / 删除
- ✅ 智能推荐算法（daily / mood / random）
- 🚧 菜品编辑（`DishDetail.vue` "编辑"按钮是 TODO）
- 🚧 图片上传（后端 `POST /dishes/{id}/image` ✅，前端无上传入口）
- 🚧 食材与步骤管理（model + schema ✅，前端缺动态表单）

### Phase 3：进阶功能（3-5天）— 🚧 15%
- 🚧 转盘抽奖（`Wheel.vue` 有页面，rotation 累加与返回结果不对应 → 假转盘）
- ❌ 盲盒翻牌组件（无路由、无页面）
- ❌ 周计划生成（`WeeklyPlan.vue` 是 TODO 空壳）
- ❌ 购物清单（无 API、无页面）

### Phase 4：完善与优化（2-3天）— 🚧 30%
- 🚧 用餐记录（API + store 完整，前端**没有任何创建入口**）
- ❌ 照片墙（`/records/timeline` API 有，前端无 UI）
- 🚧 统计面板（后端 `/stats/dashboard` OK，前端未接 ECharts）
- 🚧 响应式优化（仅 `DishDetail.vue` 写了 `@media`）
- ❌ 成就系统（model + schema 有，`AchievementService.check_achievements` 是 `pass`）

### Phase 5：部署（1天）— ✅ 100%
- ✅ Dockerfile 编写
- ✅ docker-compose 配置
- ✅ 部署到飞牛 NAS（commit `1bd834a` 修复 `host.docker.internal` 兼容性问题）
- 🚧 测试与调试（暂无自动化测试）

---

## v1.1 增量需求（基于当前代码差距 · 2026-06-07）

### 🔥 高价值 · 短工时（建议本周完成）
1. **用餐记录创建入口** — Home / DishDetail / Recommend 都加"记录这一餐"按钮 → 弹 modal 选餐型 + 评分 + 备注 → 写库。把"用餐记录"从摆设变实用的最短路径
2. **菜品编辑功能** — `DishDetail.vue` 的 TODO 落地 + 完整 ingredients / steps 动态表单（动态加/删项）
3. **菜品图片上传 UI** — Dishes 列表卡片加"上传图片"按钮，调 `POST /dishes/{id}/image`
4. **Stats 接 ECharts** — 分类分布用 pie 饼图、热门菜品用 bar 柱状图（依赖已装未用）
5. **全局错误提示** — `frontend/src/api/request.ts` 响应拦截器接 NMessage，替换裸 `console.error`

### ⚡ 中价值 · 中等工时
6. **周计划生成** — 前端可拖拽 / 后端按"近 7 天没吃 + 收藏加权"算法生成；自动汇总购物清单
7. **盲盒翻牌页** — 新路由 `mystery.vue`，3 张牌翻转动画
8. **收藏 / 已禁用筛选** — Dishes 加 NSwitch "只看收藏"/"包含已禁用"（后端 `is_favorite` / `is_enabled` filter 已支持）
9. **成就自动触发** — `create_record` 后 hook `AchievementService.check_achievements`；前端成就页加进度条
10. **MainLayout 顶部 header** — logo + 今日日期 + 欢迎语（当前是裸侧边栏）

### 🌱 长期打磨
11. **菜品配图** — 接 [TheMealDB](https://www.themealdb.com/) 免费 API 自动搜（带缓存），零成本丰富视觉
12. **转盘算法修正** — 根据返回 `dish.id` 算指针落在哪个扇区，让结果与旋转终点对齐
13. **照片墙瀑布流视图** — Records 页面 Tab 切换"列表 / 照片墙"，时间线用 masonry
14. **食材库存（pantry）** — 新表，购物清单可勾"已买到"自动入库存；库存不足时推荐自动过滤
15. **语音录入** — "今天吃了红烧肉" → 简单 nlu 匹配 `dish_id`

---

## 参考资源

- NiniMenu项目功能参考：https://github.com/TryHarder-L/NiniMenu
- FastAPI官方文档：https://fastapi.tiangolo.com/
- Naive UI组件库：https://www.naiveui.com/
- Vue3 + FastAPI全栈教程：https://github.com/tiangolo/full-stack-fastapi-postgresql

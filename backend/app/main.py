from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from .core.config import settings
from .core.database import init_db, SessionLocal
from .api.dishes import router as dishes_router
from .services.dish_service import AchievementService

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="一款温馨的家庭每日菜单推荐与食谱管理应用"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# 注册路由
app.include_router(dishes_router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库 + 种子成就定义"""
    init_db()
    # 种子写入成就定义
    db = SessionLocal()
    try:
        AchievementService(db).seed_definitions()
    finally:
        db.close()
    print(f"🍽️ {settings.APP_NAME} v{settings.APP_VERSION} 启动成功")


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

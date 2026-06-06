from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import uuid
from ..core.database import get_db
from ..core.config import settings
from ..schemas.dish import (
    DishCreate, DishUpdate, DishResponse, DishListResponse,
    RecommendResponse, MealRecordCreate, MealRecordResponse,
    DashboardStats
)
from ..services.dish_service import DishService, RecommendService, MealRecordService, AchievementService

router = APIRouter()


# 菜品相关API
@router.get("/dishes", response_model=List[DishListResponse])
def get_dishes(
    skip: int = 0,
    limit: int = 20,
    category: Optional[str] = None,
    taste: Optional[str] = None,
    is_enabled: Optional[bool] = None,
    is_favorite: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取菜品列表"""
    service = DishService(db)
    return service.get_dishes(
        skip=skip,
        limit=limit,
        category=category,
        taste=taste,
        is_enabled=is_enabled,
        is_favorite=is_favorite,
        search=search
    )


@router.get("/dishes/{dish_id}", response_model=DishResponse)
def get_dish(dish_id: int, db: Session = Depends(get_db)):
    """获取菜品详情"""
    service = DishService(db)
    dish = service.get_dish(dish_id)
    if not dish:
        raise HTTPException(status_code=404, detail="菜品不存在")
    return dish


@router.post("/dishes", response_model=DishResponse)
def create_dish(dish_data: DishCreate, db: Session = Depends(get_db)):
    """创建菜品"""
    service = DishService(db)
    return service.create_dish(dish_data)


@router.put("/dishes/{dish_id}", response_model=DishResponse)
def update_dish(dish_id: int, dish_data: DishUpdate, db: Session = Depends(get_db)):
    """更新菜品"""
    service = DishService(db)
    dish = service.update_dish(dish_id, dish_data)
    if not dish:
        raise HTTPException(status_code=404, detail="菜品不存在")
    return dish


@router.delete("/dishes/{dish_id}")
def delete_dish(dish_id: int, db: Session = Depends(get_db)):
    """删除菜品"""
    service = DishService(db)
    if not service.delete_dish(dish_id):
        raise HTTPException(status_code=404, detail="菜品不存在")
    return {"message": "删除成功"}


@router.post("/dishes/{dish_id}/image")
async def upload_dish_image(
    dish_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """上传菜品图片"""
    service = DishService(db)
    dish = service.get_dish(dish_id)
    if not dish:
        raise HTTPException(status_code=404, detail="菜品不存在")
    
    # 验证文件类型
    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="只支持 JPG、PNG、WebP 格式")
    
    # 验证文件大小
    file_size = 0
    content = await file.read()
    file_size = len(content)
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="文件大小不能超过5MB")
    
    # 生成唯一文件名
    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)
    
    # 保存文件
    with open(filepath, "wb") as f:
        f.write(content)
    
    # 更新数据库
    image_url = f"/uploads/{filename}"
    service.update_dish_image(dish_id, image_url)
    
    return {"image_url": image_url}


@router.post("/dishes/{dish_id}/favorite")
def toggle_favorite(dish_id: int, db: Session = Depends(get_db)):
    """切换收藏状态"""
    service = DishService(db)
    dish = service.toggle_favorite(dish_id)
    if not dish:
        raise HTTPException(status_code=404, detail="菜品不存在")
    return {"is_favorite": dish.is_favorite}


@router.post("/dishes/{dish_id}/enabled")
def toggle_enabled(dish_id: int, db: Session = Depends(get_db)):
    """切换启用状态"""
    service = DishService(db)
    dish = service.toggle_enabled(dish_id)
    if not dish:
        raise HTTPException(status_code=404, detail="菜品不存在")
    return {"is_enabled": dish.is_enabled}


# 推荐相关API
@router.get("/recommend/daily", response_model=RecommendResponse)
def get_daily_recommend(
    meal_type: str = "lunch",
    db: Session = Depends(get_db)
):
    """每日推荐"""
    service = RecommendService(db)
    dishes = service.get_daily_recommend(meal_type)
    return {"dishes": dishes, "meal_type": meal_type}


@router.get("/recommend/mood", response_model=RecommendResponse)
def get_mood_recommend(mood: str, db: Session = Depends(get_db)):
    """心情推荐"""
    service = RecommendService(db)
    dishes = service.get_mood_recommend(mood)
    return {"dishes": dishes, "meal_type": "mood"}


@router.get("/recommend/random")
def get_random_dish(db: Session = Depends(get_db)):
    """随机推荐（转盘用）"""
    service = RecommendService(db)
    dish = service.get_random_dish()
    if not dish:
        raise HTTPException(status_code=404, detail="没有可用的菜品")
    return dish


# 用餐记录相关API
@router.get("/records", response_model=List[MealRecordResponse])
def get_records(
    skip: int = 0,
    limit: int = 20,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """获取用餐记录"""
    service = MealRecordService(db)
    return service.get_records(skip=skip, limit=limit, start_date=start_date, end_date=end_date)


@router.post("/records", response_model=MealRecordResponse)
def create_record(record_data: MealRecordCreate, db: Session = Depends(get_db)):
    """创建用餐记录"""
    service = MealRecordService(db)
    return service.create_record(record_data)


@router.get("/records/timeline", response_model=List[MealRecordResponse])
def get_timeline(limit: int = 50, db: Session = Depends(get_db)):
    """获取时间线（照片墙用）"""
    service = MealRecordService(db)
    return service.get_timeline(limit)


# 统计相关API
@router.get("/stats/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """获取仪表盘数据"""
    from ..models.dish import Dish, MealRecord
    
    # 总菜品数
    total_dishes = db.query(Dish).count()
    
    # 总记录数
    total_records = db.query(MealRecord).count()
    
    # 分类分布
    category_stats = (
        db.query(Dish.category, func.count(Dish.id))
        .group_by(Dish.category)
        .all()
    )
    category_distribution = {cat: count for cat, count in category_stats}
    
    # 热门菜品（按记录数排序）
    top_dishes = (
        db.query(Dish.name, func.count(MealRecord.id).label("count"))
        .join(MealRecord, Dish.id == MealRecord.dish_id)
        .group_by(Dish.name)
        .order_by(desc("count"))
        .limit(10)
        .all()
    )
    top_dishes_list = [{"name": name, "count": count} for name, count in top_dishes]
    
    # 最近记录
    recent_records = (
        db.query(MealRecord)
        .order_by(desc(MealRecord.record_date))
        .limit(5)
        .all()
    )
    recent_records_list = [
        {
            "id": r.id,
            "dish_name": r.dish.name if r.dish else "未知",
            "meal_type": r.meal_type,
            "rating": r.rating,
            "record_date": r.record_date.isoformat() if r.record_date else None
        }
        for r in recent_records
    ]
    
    return {
        "total_dishes": total_dishes,
        "total_records": total_records,
        "category_distribution": category_distribution,
        "top_dishes": top_dishes_list,
        "recent_records": recent_records_list
    }


# 导入func和desc
from sqlalchemy import func, desc

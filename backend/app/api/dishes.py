from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta, date
import os
import uuid
from ..core.database import get_db
from ..core.config import settings
from ..schemas.dish import (
    DishCreate, DishUpdate, DishResponse, DishListResponse,
    RecommendResponse, MealRecordCreate, MealRecordResponse,
    DashboardStats, PantryItemCreate, PantryItemUpdate, PantryItemResponse
)
from ..models.dish import PantryItem
from ..services.dish_service import DishService, RecommendService, MealRecordService, AchievementService, WeeklyPlanService

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
    """切换收藏状态，并触发成就检查"""
    service = DishService(db)
    dish = service.toggle_favorite(dish_id)
    if not dish:
        raise HTTPException(status_code=404, detail="菜品不存在")
    AchievementService(db).check_achievements()
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
    """创建用餐记录，并触发成就检查"""
    service = MealRecordService(db)
    record = service.create_record(record_data)
    # 触发成就检查（新解锁的本次不返回，前端轮询时展示）
    AchievementService(db).check_achievements()
    return record


@router.get("/records/timeline", response_model=List[MealRecordResponse])
def get_timeline(limit: int = 50, db: Session = Depends(get_db)):
    """获取时间线（照片墙用）"""
    service = MealRecordService(db)
    return service.get_timeline(limit)


# 成就相关API
@router.get("/achievements")
def list_achievements(db: Session = Depends(get_db)):
    """获取所有成就（含解锁状态与当前进度）"""
    service = AchievementService(db)
    achs = service.get_achievements()
    progress = service.get_progress_map()
    return {
        "achievements": [
            {
                **{
                    "id": a.id,
                    "name": a.name,
                    "description": a.description,
                    "icon": a.icon,
                    "category": a.category,
                    "condition_type": a.condition_type,
                    "condition_value": a.condition_value,
                    "is_unlocked": a.is_unlocked,
                    "unlocked_at": a.unlocked_at.isoformat() if a.unlocked_at else None,
                },
                "current": progress.get(a.condition_type, 0),
            }
            for a in achs
        ],
        "progress": progress,
    }


@router.post("/achievements/check")
def trigger_achievement_check(db: Session = Depends(get_db)):
    """手动触发成就检查，返回本次新解锁的成就列表"""
    service = AchievementService(db)
    new = service.check_achievements()
    return {
        "newly_unlocked": [
            {
                "id": a.id,
                "name": a.name,
                "description": a.description,
                "icon": a.icon,
                "category": a.category,
            }
            for a in new
        ]
    }


# 周计划相关API
@router.get("/weekly-plan")
def get_weekly_plan(week_start: Optional[str] = None, db: Session = Depends(get_db)):
    """获取指定周（默认本周一）的计划；week_start 格式 YYYY-MM-DD"""
    from datetime import datetime as _dt
    if week_start:
        start = _dt.fromisoformat(week_start)
    else:
        today = _dt.now().date()
        start = _dt.combine(today - timedelta(days=today.weekday()), _dt.min.time())
    service = WeeklyPlanService(db)
    items = service.get_plan(start)
    return {
        "week_start": start.date().isoformat(),
        "items": items
    }


@router.post("/weekly-plan/generate")
def generate_weekly_plan(payload: dict = None, db: Session = Depends(get_db)):
    """生成本周（或指定周）的计划。payload: {week_start?, replace?}"""
    from datetime import datetime as _dt
    payload = payload or {}
    week_start_str = payload.get("week_start")
    replace = payload.get("replace", True)
    if week_start_str:
        week_start = _dt.fromisoformat(week_start_str)
    else:
        today = _dt.now().date()
        week_start = _dt.combine(today - timedelta(days=today.weekday()), _dt.min.time())
    service = WeeklyPlanService(db)
    items = service.generate_plan(week_start=week_start, replace=replace)
    return {
        "week_start": week_start.date().isoformat(),
        "items": items
    }


@router.patch("/weekly-plan/{plan_id}")
def swap_meal(plan_id: int, payload: dict, db: Session = Depends(get_db)):
    """替换某个餐位的菜品"""
    new_dish_id = payload.get("dish_id")
    if not new_dish_id:
        raise HTTPException(status_code=400, detail="缺少 dish_id")
    service = WeeklyPlanService(db)
    result = service.swap_meal(plan_id, new_dish_id)
    if not result:
        raise HTTPException(status_code=404, detail="餐位不存在")
    return result


@router.delete("/weekly-plan/{plan_id}")
def delete_meal(plan_id: int, db: Session = Depends(get_db)):
    """删除某个餐位"""
    service = WeeklyPlanService(db)
    if not service.remove_meal(plan_id):
        raise HTTPException(status_code=404, detail="餐位不存在")
    return {"message": "已删除"}


@router.get("/shopping-list")
def get_shopping_list(week_start: Optional[str] = None, db: Session = Depends(get_db)):
    """获取指定周的购物清单（聚合所有菜品食材）"""
    from datetime import datetime as _dt
    if week_start:
        start = _dt.fromisoformat(week_start)
    else:
        today = _dt.now().date()
        start = _dt.combine(today - timedelta(days=today.weekday()), _dt.min.time())
    service = WeeklyPlanService(db)
    return service.get_shopping_list(start)


# 食材库存 API
@router.get("/pantry", response_model=List[PantryItemResponse])
def list_pantry(
    category: Optional[str] = None,
    in_stock: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取库存列表"""
    q = db.query(PantryItem)
    if category:
        q = q.filter(PantryItem.category == category)
    if in_stock is not None:
        q = q.filter(PantryItem.in_stock == in_stock)
    if search:
        q = q.filter(PantryItem.name.contains(search))
    return q.order_by(PantryItem.category, PantryItem.name).all()


@router.post("/pantry", response_model=PantryItemResponse)
def create_pantry_item(data: PantryItemCreate, db: Session = Depends(get_db)):
    """新增库存条目"""
    item = PantryItem(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/pantry/{item_id}", response_model=PantryItemResponse)
def update_pantry_item(item_id: int, data: PantryItemUpdate, db: Session = Depends(get_db)):
    """更新库存条目"""
    item = db.query(PantryItem).filter(PantryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="库存条目不存在")
    update = data.model_dump(exclude_unset=True)
    for k, v in update.items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/pantry/{item_id}")
def delete_pantry_item(item_id: int, db: Session = Depends(get_db)):
    """删除库存条目"""
    item = db.query(PantryItem).filter(PantryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="库存条目不存在")
    db.delete(item)
    db.commit()
    return {"message": "已删除"}


@router.post("/pantry/{item_id}/toggle")
def toggle_pantry_in_stock(item_id: int, db: Session = Depends(get_db)):
    """切换 in_stock 状态（用于购物清单勾选"已买到"）"""
    item = db.query(PantryItem).filter(PantryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="库存条目不存在")
    item.in_stock = not item.in_stock
    db.commit()
    db.refresh(item)
    return {"in_stock": item.in_stock}


@router.post("/pantry/from-shopping-list")
def add_to_pantry_from_shopping(items: List[dict], db: Session = Depends(get_db)):
    """从购物清单批量加入库存：items=[{name, amount, category}]"""
    created = []
    for it in items:
        # 同名则更新，不新增
        existing = db.query(PantryItem).filter(PantryItem.name == it["name"]).first()
        if existing:
            existing.in_stock = True
            if it.get("amount"):
                existing.amount = it["amount"]
            created.append(existing.id)
        else:
            new = PantryItem(
                name=it["name"],
                amount=it.get("amount"),
                category=it.get("category") or "其它",
                in_stock=True
            )
            db.add(new)
            db.flush()
            created.append(new.id)
    db.commit()
    return {"created_ids": created, "count": len(created)}


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


# 趋势数据
@router.get("/stats/trend")
def get_stats_trend(days: int = 14, db: Session = Depends(get_db)):
    """最近 N 天每天的用餐记录数（按 date 截断到天）"""
    from ..models.dish import MealRecord

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days - 1)

    # SQL: 按 date(record_date) 分组
    date_col = func.date(MealRecord.record_date)
    rows = (
        db.query(date_col.label("d"), func.count(MealRecord.id).label("c"))
        .filter(date_col >= start_date)
        .filter(date_col <= end_date)
        .group_by("d")
        .all()
    )
    by_date = {str(d): c for d, c in rows}

    # 补齐缺失日期
    series = []
    for i in range(days):
        d = start_date + timedelta(days=i)
        ds = d.isoformat()
        series.append({"date": ds, "count": by_date.get(ds, 0)})

    return {"days": days, "series": series}


# 导入func和desc
from sqlalchemy import func, desc

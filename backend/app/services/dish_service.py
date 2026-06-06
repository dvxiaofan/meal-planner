from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta
import random
from ..models.dish import Dish, Ingredient, Step, MealRecord, WeeklyPlan, Achievement
from ..schemas.dish import DishCreate, DishUpdate, MealRecordCreate
from ..core.config import settings


class DishService:
    """菜品服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_dishes(
        self,
        skip: int = 0,
        limit: int = 20,
        category: Optional[str] = None,
        taste: Optional[str] = None,
        is_enabled: Optional[bool] = None,
        is_favorite: Optional[bool] = None,
        search: Optional[str] = None
    ) -> List[Dish]:
        """获取菜品列表"""
        query = self.db.query(Dish)
        
        if category:
            query = query.filter(Dish.category == category)
        if taste:
            query = query.filter(Dish.taste == taste)
        if is_enabled is not None:
            query = query.filter(Dish.is_enabled == is_enabled)
        if is_favorite is not None:
            query = query.filter(Dish.is_favorite == is_favorite)
        if search:
            query = query.filter(Dish.name.contains(search))
        
        return query.order_by(desc(Dish.created_at)).offset(skip).limit(limit).all()
    
    def get_dish(self, dish_id: int) -> Optional[Dish]:
        """获取菜品详情"""
        return self.db.query(Dish).filter(Dish.id == dish_id).first()
    
    def create_dish(self, dish_data: DishCreate) -> Dish:
        """创建菜品"""
        # 创建菜品
        dish = Dish(
            name=dish_data.name,
            category=dish_data.category,
            taste=dish_data.taste,
            difficulty=dish_data.difficulty,
            cook_time=dish_data.cook_time,
            description=dish_data.description
        )
        self.db.add(dish)
        self.db.flush()  # 获取ID
        
        # 创建食材
        for ingredient_data in dish_data.ingredients:
            ingredient = Ingredient(
                dish_id=dish.id,
                name=ingredient_data.name,
                amount=ingredient_data.amount,
                type=ingredient_data.type
            )
            self.db.add(ingredient)
        
        # 创建步骤
        for step_data in dish_data.steps:
            step = Step(
                dish_id=dish.id,
                step_number=step_data.step_number,
                description=step_data.description,
                duration=step_data.duration
            )
            self.db.add(step)
        
        self.db.commit()
        self.db.refresh(dish)
        return dish
    
    def update_dish(self, dish_id: int, dish_data: DishUpdate) -> Optional[Dish]:
        """更新菜品"""
        dish = self.get_dish(dish_id)
        if not dish:
            return None
        
        update_data = dish_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(dish, key, value)
        
        self.db.commit()
        self.db.refresh(dish)
        return dish
    
    def delete_dish(self, dish_id: int) -> bool:
        """删除菜品"""
        dish = self.get_dish(dish_id)
        if not dish:
            return False
        
        self.db.delete(dish)
        self.db.commit()
        return True
    
    def update_dish_image(self, dish_id: int, image_url: str) -> Optional[Dish]:
        """更新菜品图片"""
        dish = self.get_dish(dish_id)
        if not dish:
            return None
        
        dish.image_url = image_url
        self.db.commit()
        self.db.refresh(dish)
        return dish
    
    def toggle_favorite(self, dish_id: int) -> Optional[Dish]:
        """切换收藏状态"""
        dish = self.get_dish(dish_id)
        if not dish:
            return None
        
        dish.is_favorite = not dish.is_favorite
        self.db.commit()
        self.db.refresh(dish)
        return dish
    
    def toggle_enabled(self, dish_id: int) -> Optional[Dish]:
        """切换启用状态"""
        dish = self.get_dish(dish_id)
        if not dish:
            return None
        
        dish.is_enabled = not dish.is_enabled
        self.db.commit()
        self.db.refresh(dish)
        return dish


class RecommendService:
    """推荐服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_daily_recommend(self, meal_type: str = "lunch") -> List[Dish]:
        """每日推荐"""
        # 获取最近N天内吃过的菜品ID
        recent_date = datetime.now() - timedelta(days=settings.RECENT_DAYS)
        recent_dish_ids = (
            self.db.query(MealRecord.dish_id)
            .filter(MealRecord.record_date >= recent_date)
            .distinct()
            .all()
        )
        recent_dish_ids = [id for id, in recent_dish_ids]
        
        # 查询可用菜品，排除最近吃过的
        query = (
            self.db.query(Dish)
            .filter(Dish.is_enabled == True)
            .filter(Dish.id.notin_(recent_dish_ids) if recent_dish_ids else True)
        )
        
        dishes = query.all()
        
        if len(dishes) <= settings.RECOMMEND_COUNT:
            return dishes
        
        # 加权随机：收藏的菜品权重更高
        weights = []
        for dish in dishes:
            weight = 2 if dish.is_favorite else 1
            weights.append(weight)
        
        # 随机选择
        selected = random.choices(dishes, weights=weights, k=settings.RECOMMEND_COUNT)
        return selected
    
    def get_mood_recommend(self, mood: str) -> List[Dish]:
        """心情推荐"""
        mood_mapping = {
            "happy": ["清淡", "酸甜"],  # 开心
            "tired": ["清淡"],  # 疲惫
            "lazy": ["清淡"],  # 想偷懒
            "spicy": ["微辣", "中辣", "重辣", "麻辣"],  # 想吃辣
            "healthy": ["清淡"],  # 想养生
        }
        
        tastes = mood_mapping.get(mood, ["清淡"])
        
        dishes = (
            self.db.query(Dish)
            .filter(Dish.is_enabled == True)
            .filter(Dish.taste.in_(tastes))
            .all()
        )
        
        if len(dishes) <= settings.RECOMMEND_COUNT:
            return dishes
        
        return random.sample(dishes, settings.RECOMMEND_COUNT)
    
    def get_random_dish(self) -> Optional[Dish]:
        """随机推荐（转盘用）"""
        dishes = self.db.query(Dish).filter(Dish.is_enabled == True).all()
        if not dishes:
            return None
        return random.choice(dishes)


class MealRecordService:
    """用餐记录服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_records(
        self,
        skip: int = 0,
        limit: int = 20,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[MealRecord]:
        """获取用餐记录"""
        query = self.db.query(MealRecord)
        
        if start_date:
            query = query.filter(MealRecord.record_date >= start_date)
        if end_date:
            query = query.filter(MealRecord.record_date <= end_date)
        
        return query.order_by(desc(MealRecord.record_date)).offset(skip).limit(limit).all()
    
    def create_record(self, record_data: MealRecordCreate) -> MealRecord:
        """创建用餐记录"""
        record = MealRecord(
            dish_id=record_data.dish_id,
            meal_type=record_data.meal_type,
            rating=record_data.rating,
            note=record_data.note,
            record_date=record_data.record_date
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record
    
    def get_timeline(self, limit: int = 50) -> List[MealRecord]:
        """获取时间线（照片墙用）"""
        return (
            self.db.query(MealRecord)
            .filter(MealRecord.photo_url.isnot(None))
            .order_by(desc(MealRecord.record_date))
            .limit(limit)
            .all()
        )


class AchievementService:
    """成就服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_achievements(self) -> List[Achievement]:
        """获取所有成就"""
        return self.db.query(Achievement).all()
    
    def get_unlocked_achievements(self) -> List[Achievement]:
        """获取已解锁成就"""
        return self.db.query(Achievement).filter(Achievement.is_unlocked == True).all()
    
    def check_achievements(self):
        """检查并解锁成就"""
        # 这里实现成就检查逻辑
        # 根据条件类型和值检查是否满足
        pass

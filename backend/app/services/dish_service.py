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
        """更新菜品。ingredients/steps 字段若传入则整表替换（先删后建），不传则保留。"""
        dish = self.get_dish(dish_id)
        if not dish:
            return None

        update_data = dish_data.model_dump(exclude_unset=True)

        # 关联表需要单独处理，不能直接 setattr
        ingredients_payload = update_data.pop("ingredients", None)
        steps_payload = update_data.pop("steps", None)

        for key, value in update_data.items():
            setattr(dish, key, value)

        if ingredients_payload is not None:
            # 级联删除旧食材，再批量插入新的
            for old in list(dish.ingredients):
                self.db.delete(old)
            self.db.flush()
            for ing in ingredients_payload:
                self.db.add(Ingredient(
                    dish_id=dish.id,
                    name=ing["name"],
                    amount=ing.get("amount"),
                    type=ing.get("type"),
                ))

        if steps_payload is not None:
            for old in list(dish.steps):
                self.db.delete(old)
            self.db.flush()
            for i, st in enumerate(steps_payload, start=1):
                self.db.add(Step(
                    dish_id=dish.id,
                    step_number=st.get("step_number") or i,
                    description=st["description"],
                    duration=st.get("duration"),
                ))

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

    # 成就定义（启动时种子写入）
    DEFINITIONS = [
        # 用餐类
        {"name": "初入厨房", "description": "记录第一餐", "icon": "🍳", "category": "用餐", "condition_type": "meal_count", "condition_value": 1},
        {"name": "小试身手", "description": "累计记录 10 餐", "icon": "🥢", "category": "用餐", "condition_type": "meal_count", "condition_value": 10},
        {"name": "记录达人", "description": "累计记录 50 餐", "icon": "📝", "category": "用餐", "condition_type": "meal_count", "condition_value": 50},
        {"name": "百菜斩", "description": "记录 100 道不同菜品", "icon": "🏆", "category": "用餐", "condition_type": "unique_dish_count", "condition_value": 100},
        {"name": "连续一周", "description": "连续 7 天记录用餐", "icon": "📅", "category": "用餐", "condition_type": "consecutive_days", "condition_value": 7},
        {"name": "连续一月", "description": "连续 30 天记录用餐", "icon": "🗓️", "category": "用餐", "condition_type": "consecutive_days", "condition_value": 30},
        # 收藏类
        {"name": "收藏家", "description": "收藏 20 道菜品", "icon": "⭐", "category": "收藏", "condition_type": "favorite_count", "condition_value": 20},
        {"name": "美食收藏家", "description": "收藏 50 道菜品", "icon": "🌟", "category": "收藏", "condition_type": "favorite_count", "condition_value": 50},
    ]

    def __init__(self, db: Session):
        self.db = db

    def seed_definitions(self):
        """启动时种子写入成就定义（已存在则跳过）"""
        for d in self.DEFINITIONS:
            exists = self.db.query(Achievement).filter(Achievement.name == d["name"]).first()
            if not exists:
                self.db.add(Achievement(**d))
        self.db.commit()

    def get_achievements(self) -> List[Achievement]:
        return self.db.query(Achievement).order_by(Achievement.category, Achievement.condition_value).all()

    def get_unlocked_achievements(self) -> List[Achievement]:
        return self.db.query(Achievement).filter(Achievement.is_unlocked == True).all()

    def get_progress_map(self) -> dict:
        """返回每个 condition_type 的当前进度值"""
        progress = {}
        # 餐记录数
        progress["meal_count"] = self.db.query(MealRecord).count()
        # 不同菜品数
        progress["unique_dish_count"] = self.db.query(MealRecord.dish_id).distinct().count()
        # 收藏数
        from ..models.dish import Dish
        progress["favorite_count"] = self.db.query(Dish).filter(Dish.is_favorite == True).count()
        # 连续天数（最长连续有记录的天数）
        progress["consecutive_days"] = self._calc_consecutive_days()
        return progress

    def _calc_consecutive_days(self) -> int:
        """从今天往前算，连续有记录的最大天数"""
        from ..models.dish import Dish
        from datetime import date as _date
        rows = (
            self.db.query(func.date(MealRecord.record_date).label("d"))
            .distinct()
            .order_by(desc("d"))
            .all()
        )
        # SQLite 的 func.date() 返回字符串，统一转 date 对象
        date_list: list = []
        for r in rows:
            v = r[0]
            if isinstance(v, str):
                date_list.append(_date.fromisoformat(v))
            elif isinstance(v, _date):
                date_list.append(v)
            else:
                continue
        if not date_list:
            return 0
        # 必须包含今天或昨天才算"当前连续"
        today = _date.today()
        start = date_list[0]
        if (today - start).days > 1:
            return 0
        # 连续计数
        count = 1
        for i in range(1, len(date_list)):
            if (date_list[i - 1] - date_list[i]).days == 1:
                count += 1
            else:
                break
        return count

    def check_achievements(self) -> List[Achievement]:
        """检查并解锁满足条件的成就，返回本次新解锁的"""
        progress = self.get_progress_map()
        newly_unlocked: List[Achievement] = []
        all_achievements = self.db.query(Achievement).all()
        for ach in all_achievements:
            if ach.is_unlocked:
                continue
            current = progress.get(ach.condition_type, 0)
            if current >= ach.condition_value:
                ach.is_unlocked = True
                ach.unlocked_at = datetime.now()
                newly_unlocked.append(ach)
        if newly_unlocked:
            self.db.commit()
        return newly_unlocked


class WeeklyPlanService:
    """周计划 + 购物清单服务"""

    MEAL_TYPES = ["lunch", "dinner"]

    def __init__(self, db: Session):
        self.db = db

    def get_plan(self, week_start: datetime) -> List[dict]:
        """获取指定周起始的 14 个餐位（7 天 × 午晚餐）"""
        from ..models.dish import WeeklyPlan
        # week_start 归零到天
        start_date = week_start.date() if isinstance(week_start, datetime) else week_start
        rows = (
            self.db.query(WeeklyPlan)
            .filter(func.date(WeeklyPlan.week_start) == start_date)
            .order_by(WeeklyPlan.day_of_week, WeeklyPlan.meal_type)
            .all()
        )
        out = []
        for r in rows:
            dish = self.db.query(Dish).filter(Dish.id == r.dish_id).first()
            out.append({
                "id": r.id,
                "week_start": r.week_start.isoformat(),
                "day_of_week": r.day_of_week,
                "meal_type": r.meal_type,
                "dish": self._dish_summary(dish) if dish else None
            })
        return out

    def _dish_summary(self, dish: Dish) -> dict:
        return {
            "id": dish.id, "name": dish.name, "category": dish.category,
            "taste": dish.taste, "difficulty": dish.difficulty,
            "cook_time": dish.cook_time, "image_url": dish.image_url,
            "is_favorite": dish.is_favorite, "is_enabled": dish.is_enabled
        }

    def generate_plan(self, week_start: Optional[datetime] = None, replace: bool = True) -> List[dict]:
        """按"近 7 天没吃 + 收藏加权 + 不重复同周"算法生成本周 14 个餐位
        - replace=True 时先清空该周
        - 返回生成结果
        """
        from ..models.dish import WeeklyPlan
        if week_start is None:
            today = datetime.now().date()
            week_start = datetime.combine(today - timedelta(days=today.weekday()), datetime.min.time())

        start_date = week_start.date() if isinstance(week_start, datetime) else week_start

        if replace:
            self.db.query(WeeklyPlan).filter(func.date(WeeklyPlan.week_start) == start_date).delete()
            self.db.commit()

        # 候选菜品：仅启用的
        candidates = self.db.query(Dish).filter(Dish.is_enabled == True).all()
        if not candidates:
            return []

        # 已吃过的：最近 7 天
        recent_cutoff = datetime.now() - timedelta(days=7)
        recent_ids = {
            r[0] for r in
            self.db.query(MealRecord.dish_id)
            .filter(MealRecord.record_date >= recent_cutoff)
            .distinct().all()
        }

        # 池子：排除最近吃过
        pool = [d for d in candidates if d.id not in recent_ids]
        if not pool:
            pool = candidates  # 退而求其次，用全部

        # 14 个槽位
        slots = [(dow, mt) for dow in range(1, 8) for mt in self.MEAL_TYPES]
        used: set = set()
        generated = []

        for dow, meal_type in slots:
            available = [d for d in pool if d.id not in used]
            if not available:
                # 所有菜都用过了，重置 used 允许重复
                used.clear()
                available = pool
            weights = [2 if d.is_favorite else 1 for d in available]
            chosen = random.choices(available, weights=weights, k=1)[0]
            used.add(chosen.id)
            plan = WeeklyPlan(
                week_start=week_start,
                day_of_week=dow,
                meal_type=meal_type,
                dish_id=chosen.id
            )
            self.db.add(plan)
            self.db.flush()
            generated.append({
                "id": plan.id,
                "week_start": plan.week_start.isoformat(),
                "day_of_week": dow,
                "meal_type": meal_type,
                "dish": self._dish_summary(chosen)
            })

        self.db.commit()
        return generated

    def swap_meal(self, plan_id: int, new_dish_id: int) -> Optional[dict]:
        """替换某个餐位的菜品"""
        from ..models.dish import WeeklyPlan
        plan = self.db.query(WeeklyPlan).filter(WeeklyPlan.id == plan_id).first()
        if not plan:
            return None
        plan.dish_id = new_dish_id
        self.db.commit()
        self.db.refresh(plan)
        dish = self.db.query(Dish).filter(Dish.id == new_dish_id).first()
        return {
            "id": plan.id,
            "week_start": plan.week_start.isoformat(),
            "day_of_week": plan.day_of_week,
            "meal_type": plan.meal_type,
            "dish": self._dish_summary(dish) if dish else None
        }

    def remove_meal(self, plan_id: int) -> bool:
        from ..models.dish import WeeklyPlan
        plan = self.db.query(WeeklyPlan).filter(WeeklyPlan.id == plan_id).first()
        if not plan:
            return False
        self.db.delete(plan)
        self.db.commit()
        return True

    def get_shopping_list(self, week_start: datetime) -> dict:
        """聚合指定周所有菜品的食材，按食材名合并用量"""
        from ..models.dish import WeeklyPlan
        start_date = week_start.date() if isinstance(week_start, datetime) else week_start
        plans = (
            self.db.query(WeeklyPlan)
            .filter(func.date(WeeklyPlan.week_start) == start_date)
            .all()
        )
        if not plans:
            return {"week_start": start_date.isoformat(), "by_category": {}, "items": []}

        # 取所有相关菜品及其 ingredients
        dish_ids = [p.dish_id for p in plans]
        dishes = self.db.query(Dish).filter(Dish.id.in_(dish_ids)).all()
        dish_map = {d.id: d for d in dishes}

        items_map: dict = {}  # name -> {name, amount_total, type, used_in: [dish_names]}
        for plan in plans:
            dish = dish_map.get(plan.dish_id)
            if not dish:
                continue
            for ing in (dish.ingredients or []):
                key = ing.name.strip()
                if not key:
                    continue
                if key not in items_map:
                    items_map[key] = {
                        "name": key,
                        "amounts": [],
                        "type": ing.type,
                        "used_in": []
                    }
                if ing.amount:
                    items_map[key]["amounts"].append(ing.amount)
                items_map[key]["used_in"].append(dish.name)

        # 按 type 分组（主料/调料/其它）
        by_category: dict = {}
        for it in items_map.values():
            cat = it.get("type") or "其它"
            by_category.setdefault(cat, []).append(it)

        # 排序：主料 → 调料
        items = list(items_map.values())
        return {
            "week_start": start_date.isoformat(),
            "by_category": by_category,
            "items": items
        }

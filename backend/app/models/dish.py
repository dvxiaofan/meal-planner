from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base


class Dish(Base):
    """菜品表"""
    __tablename__ = "dishes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    category = Column(String(50), nullable=False)  # 荤菜/素菜/汤/主食/凉菜/小吃
    taste = Column(String(50))  # 清淡/微辣/中辣/重辣/酸甜/咸鲜/麻辣/酸辣/五香/蒜香
    difficulty = Column(Integer, default=1)  # 1-5
    cook_time = Column(Integer)  # 分钟
    is_enabled = Column(Boolean, default=True)
    is_favorite = Column(Boolean, default=False)
    image_url = Column(String(500))
    video_url = Column(String(500))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关联
    ingredients = relationship("Ingredient", back_populates="dish", cascade="all, delete-orphan")
    steps = relationship("Step", back_populates="dish", cascade="all, delete-orphan")
    meal_records = relationship("MealRecord", back_populates="dish")


class Ingredient(Base):
    """食材表"""
    __tablename__ = "ingredients"
    
    id = Column(Integer, primary_key=True, index=True)
    dish_id = Column(Integer, ForeignKey("dishes.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    amount = Column(String(50))  # 如"200g"
    type = Column(String(20))  # 主料/调料
    
    dish = relationship("Dish", back_populates="ingredients")


class Step(Base):
    """烹饪步骤表"""
    __tablename__ = "steps"
    
    id = Column(Integer, primary_key=True, index=True)
    dish_id = Column(Integer, ForeignKey("dishes.id", ondelete="CASCADE"), nullable=False)
    step_number = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    duration = Column(Integer)  # 秒
    
    dish = relationship("Dish", back_populates="steps")


class MealRecord(Base):
    """用餐记录表"""
    __tablename__ = "meal_records"
    
    id = Column(Integer, primary_key=True, index=True)
    dish_id = Column(Integer, ForeignKey("dishes.id"), nullable=False)
    meal_type = Column(String(20), nullable=False)  # 午餐/晚餐
    rating = Column(Integer)  # 1-5
    note = Column(Text)
    photo_url = Column(String(500))
    record_date = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now)
    
    dish = relationship("Dish", back_populates="meal_records")


class WeeklyPlan(Base):
    """周计划表"""
    __tablename__ = "weekly_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    week_start = Column(DateTime, nullable=False, index=True)
    day_of_week = Column(Integer, nullable=False)  # 1-7
    meal_type = Column(String(20), nullable=False)  # 午餐/晚餐
    dish_id = Column(Integer, ForeignKey("dishes.id"), nullable=False)
    
    dish = relationship("Dish")


class Achievement(Base):
    """成就表"""
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    icon = Column(String(50))
    category = Column(String(50))  # 用餐/心情/推荐/收藏/记录
    condition_type = Column(String(50))
    condition_value = Column(Integer)
    is_unlocked = Column(Boolean, default=False)
    unlocked_at = Column(DateTime)


class PantryItem(Base):
    """食材库存表"""
    __tablename__ = "pantry_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    amount = Column(String(50))
    unit = Column(String(20))
    category = Column(String(50))
    note = Column(Text)
    expires_at = Column(DateTime)  # 过期时间（可选）
    in_stock = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class UsageCounter(Base):
    """使用次数计数器（转盘/盲盒/心情等）"""
    __tablename__ = "usage_counters"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(50), unique=True, nullable=False, index=True)
    count = Column(Integer, default=0, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

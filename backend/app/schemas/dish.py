from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# 食材schemas
class IngredientBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="食材名称")
    amount: Optional[str] = Field(None, max_length=50, description="用量")
    type: Optional[str] = Field(None, max_length=20, description="类型（主料/调料）")


class IngredientCreate(IngredientBase):
    pass


class IngredientResponse(IngredientBase):
    id: int
    dish_id: int
    
    class Config:
        from_attributes = True


# 步骤schemas
class StepBase(BaseModel):
    step_number: int = Field(..., ge=1, description="步骤序号")
    description: str = Field(..., min_length=1, description="步骤描述")
    duration: Optional[int] = Field(None, ge=0, description="计时（秒）")


class StepCreate(StepBase):
    pass


class StepResponse(StepBase):
    id: int
    dish_id: int
    
    class Config:
        from_attributes = True


# 菜品schemas
class DishBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="菜品名称")
    category: str = Field(..., description="分类（荤菜/素菜/汤/主食/凉菜/小吃）")
    taste: Optional[str] = Field(None, description="口味")
    difficulty: int = Field(1, ge=1, le=5, description="难度（1-5）")
    cook_time: Optional[int] = Field(None, ge=0, description="烹饪时间（分钟）")
    description: Optional[str] = Field(None, description="简介")


class DishCreate(DishBase):
    ingredients: List[IngredientCreate] = []
    steps: List[StepCreate] = []


class DishUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[str] = None
    taste: Optional[str] = None
    difficulty: Optional[int] = Field(None, ge=1, le=5)
    cook_time: Optional[int] = Field(None, ge=0)
    is_enabled: Optional[bool] = None
    is_favorite: Optional[bool] = None
    description: Optional[str] = None


class DishResponse(DishBase):
    id: int
    is_enabled: bool
    is_favorite: bool
    image_url: Optional[str]
    video_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    ingredients: List[IngredientResponse] = []
    steps: List[StepResponse] = []
    
    class Config:
        from_attributes = True


class DishListResponse(BaseModel):
    id: int
    name: str
    category: str
    taste: Optional[str]
    difficulty: int
    cook_time: Optional[int]
    is_enabled: bool
    is_favorite: bool
    image_url: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# 推荐相关
class RecommendResponse(BaseModel):
    dishes: List[DishListResponse]
    meal_type: str


# 用餐记录schemas
class MealRecordBase(BaseModel):
    dish_id: int
    meal_type: str = Field(..., description="午餐/晚餐")
    rating: Optional[int] = Field(None, ge=1, le=5, description="评分（1-5）")
    note: Optional[str] = None
    record_date: datetime


class MealRecordCreate(MealRecordBase):
    pass


class MealRecordResponse(MealRecordBase):
    id: int
    photo_url: Optional[str]
    created_at: datetime
    dish: DishListResponse
    
    class Config:
        from_attributes = True


# 周计划schemas
class WeeklyPlanBase(BaseModel):
    week_start: datetime
    day_of_week: int = Field(..., ge=1, le=7, description="星期几（1-7）")
    meal_type: str = Field(..., description="午餐/晚餐")
    dish_id: int


class WeeklyPlanCreate(WeeklyPlanBase):
    pass


class WeeklyPlanResponse(WeeklyPlanBase):
    id: int
    dish: DishListResponse
    
    class Config:
        from_attributes = True


# 成就schemas
class AchievementResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    icon: Optional[str]
    category: Optional[str]
    condition_type: Optional[str]
    condition_value: Optional[int]
    is_unlocked: bool
    unlocked_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# 统计相关
class DashboardStats(BaseModel):
    total_dishes: int
    total_records: int
    category_distribution: dict
    top_dishes: List[dict]
    recent_records: List[dict]

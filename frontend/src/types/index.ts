// 菜品类型
export interface Dish {
  id: number
  name: string
  category: string
  taste?: string
  difficulty: number
  cook_time?: number
  is_enabled: boolean
  is_favorite: boolean
  image_url?: string
  video_url?: string
  description?: string
  created_at: string
  updated_at: string
  ingredients?: Ingredient[]
  steps?: Step[]
}

export interface DishCreate {
  name: string
  category: string
  taste?: string
  difficulty?: number
  cook_time?: number
  description?: string
  ingredients?: IngredientCreate[]
  steps?: StepCreate[]
}

export interface DishUpdate {
  name?: string
  category?: string
  taste?: string
  difficulty?: number
  cook_time?: number
  is_enabled?: boolean
  is_favorite?: boolean
  description?: string
  ingredients?: IngredientCreate[]
  steps?: StepCreate[]
}

// 食材类型
export interface Ingredient {
  id: number
  dish_id: number
  name: string
  amount?: string
  type?: string
}

export interface IngredientCreate {
  name: string
  amount?: string
  type?: string
}

// 步骤类型
export interface Step {
  id: number
  dish_id: number
  step_number: number
  description: string
  duration?: number
}

export interface StepCreate {
  step_number: number
  description: string
  duration?: number
}

// 推荐响应
export interface RecommendResponse {
  dishes: Dish[]
  meal_type: string
}

// 用餐记录
export interface MealRecord {
  id: number
  dish_id: number
  meal_type: string
  rating?: number
  note?: string
  photo_url?: string
  record_date: string
  created_at: string
  dish: Dish
}

// 仪表盘统计
export interface DashboardStats {
  total_dishes: number
  total_records: number
  category_distribution: Record<string, number>
  top_dishes: Array<{ name: string; count: number }>
  recent_records: Array<{
    id: number
    dish_name: string
    meal_type: string
    rating?: number
    record_date?: string
  }>
}

// 成就
export interface Achievement {
  id: number
  name: string
  description?: string
  icon?: string
  category?: string
  condition_type?: string
  condition_value?: number
  is_unlocked: boolean
  unlocked_at?: string | null
  current?: number
}

export interface AchievementsResponse {
  achievements: Achievement[]
  progress: Record<string, number>
}

// 周计划
export interface WeeklyPlanItem {
  id: number
  week_start: string
  day_of_week: number  // 1-7
  meal_type: 'lunch' | 'dinner'
  dish: Dish | null
}

export interface WeeklyPlanResponse {
  week_start: string
  items: WeeklyPlanItem[]
}

// 购物清单
export interface ShoppingListItem {
  name: string
  amounts: string[]
  type?: string
  used_in: string[]
}

export interface ShoppingListResponse {
  week_start: string
  by_category: Record<string, ShoppingListItem[]>
  items: ShoppingListItem[]
}

// 库存
export interface PantryItem {
  id: number
  name: string
  amount?: string
  unit?: string
  category?: string
  note?: string
  expires_at?: string | null
  in_stock: boolean
  created_at: string
  updated_at: string
}

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

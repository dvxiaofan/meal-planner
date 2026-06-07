import request from './request'
import type {
  Dish, DishCreate, DishUpdate, RecommendResponse, MealRecord,
  DashboardStats, AchievementsResponse,
  WeeklyPlanResponse, WeeklyPlanItem, ShoppingListResponse, PantryItem
} from '@/types'

// 菜品相关API
export const dishApi = {
  getDishes(params?: {
    skip?: number
    limit?: number
    category?: string
    taste?: string
    is_enabled?: boolean
    is_favorite?: boolean
    search?: string
  }) {
    return request.get<any, Dish[]>('/dishes', { params })
  },

  getDish(id: number) {
    return request.get<any, Dish>(`/dishes/${id}`)
  },

  createDish(data: DishCreate) {
    return request.post<any, Dish>('/dishes', data)
  },

  updateDish(id: number, data: DishUpdate) {
    return request.put<any, Dish>(`/dishes/${id}`, data)
  },

  deleteDish(id: number) {
    return request.delete(`/dishes/${id}`)
  },

  uploadImage(id: number, file: File) {
    const formData = new FormData()
    formData.append('file', file)
    return request.post<any, { image_url: string }>(`/dishes/${id}/image`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  toggleFavorite(id: number) {
    return request.post<any, { is_favorite: boolean }>(`/dishes/${id}/favorite`)
  },

  toggleEnabled(id: number) {
    return request.post<any, { is_enabled: boolean }>(`/dishes/${id}/enabled`)
  }
}

// 推荐相关API
export const recommendApi = {
  getDailyRecommend(mealType: string = 'lunch') {
    return request.get<any, RecommendResponse>('/recommend/daily', {
      params: { meal_type: mealType }
    })
  },

  getMoodRecommend(mood: string) {
    return request.get<any, RecommendResponse>('/recommend/mood', {
      params: { mood }
    })
  },

  getRandomDish() {
    return request.get<any, Dish>('/recommend/random')
  }
}

// 用餐记录相关API
export const recordApi = {
  getRecords(params?: {
    skip?: number
    limit?: number
    start_date?: string
    end_date?: string
  }) {
    return request.get<any, MealRecord[]>('/records', { params })
  },

  createRecord(data: {
    dish_id: number
    meal_type: string
    rating?: number
    note?: string
    record_date: string
  }) {
    return request.post<any, MealRecord>('/records', data)
  },

  getTimeline(limit: number = 50) {
    return request.get<any, MealRecord[]>('/records/timeline', {
      params: { limit }
    })
  },

  uploadPhoto(recordId: number, formData: FormData) {
    return request.post<any, { photo_url: string }>(
      `/records/${recordId}/photo`,
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    )
  }
}

// 统计相关API
export const statsApi = {
  getDashboardStats() {
    return request.get<any, DashboardStats>('/stats/dashboard')
  },
  getTrend(days: number = 14) {
    return request.get<any, { days: number; series: Array<{ date: string; count: number }> }>(
      '/stats/trend',
      { params: { days } }
    )
  },
  getBreakdown() {
    return request.get<any, {
      by_taste: Record<string, number>
      by_category_records: Record<string, number>
      weekly: Array<{ label: string; count: number }>
      category_trend: { dates: string[]; series: Array<{ name: string; data: number[] }> }
    }>('/stats/breakdown')
  }
}

// 成就相关API
export const achievementApi = {
  list() {
    return request.get<any, AchievementsResponse>('/achievements')
  },
  check() {
    return request.post<any, { newly_unlocked: Array<{ id: number; name: string; description?: string; icon?: string; category?: string }> }>('/achievements/check')
  }
}

// 周计划API
export const weeklyPlanApi = {
  get(week_start?: string) {
    return request.get<any, WeeklyPlanResponse>('/weekly-plan', {
      params: week_start ? { week_start } : {}
    })
  },
  generate(payload: { week_start?: string; replace?: boolean } = {}) {
    return request.post<any, WeeklyPlanResponse>('/weekly-plan/generate', payload)
  },
  swap(planId: number, dishId: number) {
    return request.patch<any, WeeklyPlanItem>(`/weekly-plan/${planId}`, { dish_id: dishId })
  },
  swapPositions(planId1: number, planId2: number) {
    return request.post<any, { items: WeeklyPlanItem[] }>('/weekly-plan/swap-positions', {
      plan_id_1: planId1, plan_id_2: planId2
    })
  },
  remove(planId: number) {
    return request.delete(`/weekly-plan/${planId}`)
  },
  shoppingList(week_start?: string) {
    return request.get<any, ShoppingListResponse>('/shopping-list', {
      params: week_start ? { week_start } : {}
    })
  }
}

// 库存 API
export const pantryApi = {
  list(params?: { category?: string; in_stock?: boolean; search?: string }) {
    return request.get<any, PantryItem[]>('/pantry', { params })
  },
  create(data: Omit<PantryItem, 'id' | 'created_at' | 'updated_at'>) {
    return request.post<any, PantryItem>('/pantry', data)
  },
  update(id: number, data: Partial<PantryItem>) {
    return request.put<any, PantryItem>(`/pantry/${id}`, data)
  },
  remove(id: number) {
    return request.delete(`/pantry/${id}`)
  },
  toggleInStock(id: number) {
    return request.post<any, { in_stock: boolean }>(`/pantry/${id}/toggle`)
  },
  addFromShoppingList(items: Array<{ name: string; amount?: string; category?: string }>) {
    return request.post<any, { count: number; created_ids: number[] }>('/pantry/from-shopping-list', items)
  }
}

// 使用次数 API（盲盒/转盘/心情）
export const usageApi = {
  increment(key: string, delta: number = 1) {
    return request.post<any, { key: string; count: number; newly_unlocked: Array<{ id: number; name: string }> }>(
      '/usage/increment', { key, delta }
    )
  },
  stats() {
    return request.get<any, { stats: Array<{ key: string; count: number }> }>('/usage/stats')
  }
}

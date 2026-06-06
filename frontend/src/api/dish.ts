import request from './request'
import type { Dish, DishCreate, DishUpdate, RecommendResponse, MealRecord, DashboardStats } from '@/types'

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
  }
}

// 统计相关API
export const statsApi = {
  getDashboardStats() {
    return request.get<any, DashboardStats>('/stats/dashboard')
  }
}

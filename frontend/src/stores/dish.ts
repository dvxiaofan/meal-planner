import { defineStore } from 'pinia'
import { ref } from 'vue'
import { dishApi } from '@/api/dish'
import type { Dish, DishCreate, DishUpdate } from '@/types'

export const useDishStore = defineStore('dish', () => {
  const dishes = ref<Dish[]>([])
  const currentDish = ref<Dish | null>(null)
  const loading = ref(false)
  const total = ref(0)

  // 获取菜品列表
  async function fetchDishes(params?: {
    skip?: number
    limit?: number
    category?: string
    taste?: string
    is_enabled?: boolean
    is_favorite?: boolean
    search?: string
  }) {
    loading.value = true
    try {
      const data = await dishApi.getDishes(params)
      dishes.value = data
      return data
    } catch (error) {
      console.error('获取菜品列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取菜品详情
  async function fetchDish(id: number) {
    loading.value = true
    try {
      const data = await dishApi.getDish(id)
      currentDish.value = data
      return data
    } catch (error) {
      console.error('获取菜品详情失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 创建菜品
  async function createDish(data: DishCreate) {
    loading.value = true
    try {
      const newDish = await dishApi.createDish(data)
      dishes.value.unshift(newDish)
      return newDish
    } catch (error) {
      console.error('创建菜品失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 更新菜品
  async function updateDish(id: number, data: DishUpdate) {
    loading.value = true
    try {
      const updatedDish = await dishApi.updateDish(id, data)
      const index = dishes.value.findIndex(d => d.id === id)
      if (index !== -1) {
        dishes.value[index] = updatedDish
      }
      if (currentDish.value?.id === id) {
        currentDish.value = updatedDish
      }
      return updatedDish
    } catch (error) {
      console.error('更新菜品失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 删除菜品
  async function deleteDish(id: number) {
    loading.value = true
    try {
      await dishApi.deleteDish(id)
      dishes.value = dishes.value.filter(d => d.id !== id)
      if (currentDish.value?.id === id) {
        currentDish.value = null
      }
    } catch (error) {
      console.error('删除菜品失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 上传图片
  async function uploadImage(id: number, file: File) {
    try {
      const { image_url } = await dishApi.uploadImage(id, file)
      const index = dishes.value.findIndex(d => d.id === id)
      if (index !== -1) {
        dishes.value[index].image_url = image_url
      }
      if (currentDish.value?.id === id) {
        currentDish.value.image_url = image_url
      }
      return image_url
    } catch (error) {
      console.error('上传图片失败:', error)
      throw error
    }
  }

  // 切换收藏
  async function toggleFavorite(id: number) {
    try {
      const { is_favorite } = await dishApi.toggleFavorite(id)
      const index = dishes.value.findIndex(d => d.id === id)
      if (index !== -1) {
        dishes.value[index].is_favorite = is_favorite
      }
      if (currentDish.value?.id === id) {
        currentDish.value.is_favorite = is_favorite
      }
      return is_favorite
    } catch (error) {
      console.error('切换收藏失败:', error)
      throw error
    }
  }

  // 切换启用
  async function toggleEnabled(id: number) {
    try {
      const { is_enabled } = await dishApi.toggleEnabled(id)
      const index = dishes.value.findIndex(d => d.id === id)
      if (index !== -1) {
        dishes.value[index].is_enabled = is_enabled
      }
      if (currentDish.value?.id === id) {
        currentDish.value.is_enabled = is_enabled
      }
      return is_enabled
    } catch (error) {
      console.error('切换启用失败:', error)
      throw error
    }
  }

  return {
    dishes,
    currentDish,
    loading,
    total,
    fetchDishes,
    fetchDish,
    createDish,
    updateDish,
    deleteDish,
    uploadImage,
    toggleFavorite,
    toggleEnabled
  }
})

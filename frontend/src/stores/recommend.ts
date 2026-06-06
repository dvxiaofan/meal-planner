import { defineStore } from 'pinia'
import { ref } from 'vue'
import { recommendApi } from '@/api/dish'
import type { Dish } from '@/types'

export const useRecommendStore = defineStore('recommend', () => {
  const dailyDishes = ref<Dish[]>([])
  const moodDishes = ref<Dish[]>([])
  const randomDish = ref<Dish | null>(null)
  const loading = ref(false)

  // 每日推荐
  async function fetchDailyRecommend(mealType: string = 'lunch') {
    loading.value = true
    try {
      const { dishes } = await recommendApi.getDailyRecommend(mealType)
      dailyDishes.value = dishes
      return dishes
    } catch (error) {
      console.error('获取每日推荐失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 心情推荐
  async function fetchMoodRecommend(mood: string) {
    loading.value = true
    try {
      const { dishes } = await recommendApi.getMoodRecommend(mood)
      moodDishes.value = dishes
      return dishes
    } catch (error) {
      console.error('获取心情推荐失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 随机推荐
  async function fetchRandomDish() {
    loading.value = true
    try {
      const dish = await recommendApi.getRandomDish()
      randomDish.value = dish
      return dish
    } catch (error) {
      console.error('获取随机推荐失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  return {
    dailyDishes,
    moodDishes,
    randomDish,
    loading,
    fetchDailyRecommend,
    fetchMoodRecommend,
    fetchRandomDish
  }
})

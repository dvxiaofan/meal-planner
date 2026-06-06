import { defineStore } from 'pinia'
import { ref } from 'vue'
import { recordApi } from '@/api/dish'
import type { MealRecord } from '@/types'

export const useRecordStore = defineStore('record', () => {
  const records = ref<MealRecord[]>([])
  const timeline = ref<MealRecord[]>([])
  const loading = ref(false)

  // 获取用餐记录
  async function fetchRecords(params?: {
    skip?: number
    limit?: number
    start_date?: string
    end_date?: string
  }) {
    loading.value = true
    try {
      const data = await recordApi.getRecords(params)
      records.value = data
      return data
    } catch (error) {
      console.error('获取用餐记录失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 创建用餐记录
  async function createRecord(data: {
    dish_id: number
    meal_type: string
    rating?: number
    note?: string
    record_date: string
  }) {
    loading.value = true
    try {
      const newRecord = await recordApi.createRecord(data)
      records.value.unshift(newRecord)
      return newRecord
    } catch (error) {
      console.error('创建用餐记录失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取时间线
  async function fetchTimeline(limit: number = 50) {
    loading.value = true
    try {
      const data = await recordApi.getTimeline(limit)
      timeline.value = data
      return data
    } catch (error) {
      console.error('获取时间线失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  return {
    records,
    timeline,
    loading,
    fetchRecords,
    createRecord,
    fetchTimeline
  }
})

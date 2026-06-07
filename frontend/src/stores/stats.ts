import { defineStore } from 'pinia'
import { ref } from 'vue'
import { statsApi } from '@/api/dish'
import type { DashboardStats } from '@/types'

export interface TrendPoint {
  date: string
  count: number
}

export const useStatsStore = defineStore('stats', () => {
  const dashboard = ref<DashboardStats | null>(null)
  const trend = ref<TrendPoint[]>([])
  const loading = ref(false)

  async function fetchDashboardStats() {
    loading.value = true
    try {
      const data = await statsApi.getDashboardStats()
      dashboard.value = data
      return data
    } catch (error) {
      throw error
    } finally {
      loading.value = false
    }
  }

  async function fetchTrend(days: number = 14) {
    try {
      const data = await statsApi.getTrend(days)
      trend.value = data.series
      return data.series
    } catch (error) {
      throw error
    }
  }

  return {
    dashboard,
    trend,
    loading,
    fetchDashboardStats,
    fetchTrend
  }
})

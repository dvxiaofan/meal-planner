import { defineStore } from 'pinia'
import { ref } from 'vue'
import { statsApi } from '@/api/dish'
import type { DashboardStats } from '@/types'

export const useStatsStore = defineStore('stats', () => {
  const dashboard = ref<DashboardStats | null>(null)
  const loading = ref(false)

  // 获取仪表盘数据
  async function fetchDashboardStats() {
    loading.value = true
    try {
      const data = await statsApi.getDashboardStats()
      dashboard.value = data
      return data
    } catch (error) {
      console.error('获取仪表盘数据失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  return {
    dashboard,
    loading,
    fetchDashboardStats
  }
})

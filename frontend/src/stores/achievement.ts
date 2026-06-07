import { defineStore } from 'pinia'
import { ref } from 'vue'
import { achievementApi } from '@/api/dish'
import type { Achievement, AchievementsResponse } from '@/types'

export const useAchievementStore = defineStore('achievement', () => {
  const achievements = ref<Achievement[]>([])
  const progress = ref<Record<string, number>>({})
  const loading = ref(false)

  async function fetchList() {
    loading.value = true
    try {
      const data: AchievementsResponse = await achievementApi.list()
      achievements.value = data.achievements
      progress.value = data.progress
      return data
    } finally {
      loading.value = false
    }
  }

  async function triggerCheck() {
    const { newly_unlocked } = await achievementApi.check()
    if (newly_unlocked.length > 0) {
      await fetchList()
    }
    return newly_unlocked
  }

  return {
    achievements,
    progress,
    loading,
    fetchList,
    triggerCheck
  }
})
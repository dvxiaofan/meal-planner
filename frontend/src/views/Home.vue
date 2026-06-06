<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { NCard, NGrid, NGi, NStatistic, NButton, NSpace, NTag, NEmpty } from 'naive-ui'
import { useStatsStore, useRecommendStore } from '@/stores'
import type { Dish } from '@/types'

const router = useRouter()
const statsStore = useStatsStore()
const recommendStore = useRecommendStore()

const todayRecommend = ref<Dish[]>([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([
      statsStore.fetchDashboardStats(),
      recommendStore.fetchDailyRecommend('lunch')
    ])
    todayRecommend.value = recommendStore.dailyDishes
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.value = false
  }
})

function goToDishes() {
  router.push({ name: 'dishes' })
}

function goToRecommend() {
  router.push({ name: 'recommend' })
}

function goToRecords() {
  router.push({ name: 'records' })
}
</script>

<template>
  <div class="page-container">
    <h1 class="page-title">欢迎使用食光 🍽️</h1>
    
    <!-- 统计卡片 -->
    <NGrid :cols="4" :x-gap="16" :y-gap="16" style="margin-bottom: 24px">
      <NGi>
        <NCard>
          <NStatistic label="菜品总数" :value="statsStore.dashboard?.total_dishes || 0" />
        </NCard>
      </NGi>
      <NGi>
        <NCard>
          <NStatistic label="用餐记录" :value="statsStore.dashboard?.total_records || 0" />
        </NCard>
      </NGi>
      <NGi>
        <NCard>
          <NStatistic label="今日推荐" :value="todayRecommend.length" />
        </NCard>
      </NGi>
      <NGi>
        <NCard>
          <NStatistic label="成就解锁" :value="0" />
        </NCard>
      </NGi>
    </NGrid>

    <!-- 今日推荐 -->
    <NCard title="今日推荐" style="margin-bottom: 24px">
      <template #header-extra>
        <NButton text type="primary" @click="goToRecommend">查看更多</NButton>
      </template>
      
      <div v-if="todayRecommend.length > 0" class="recommend-list">
        <NCard v-for="dish in todayRecommend" :key="dish.id" class="dish-card">
          <div class="dish-info">
            <h3>{{ dish.name }}</h3>
            <NSpace>
              <NTag v-if="dish.category" size="small">{{ dish.category }}</NTag>
              <NTag v-if="dish.taste" size="small" type="info">{{ dish.taste }}</NTag>
            </NSpace>
          </div>
        </NCard>
      </div>
      <NEmpty v-else description="暂无推荐" />
    </NCard>

    <!-- 快捷操作 -->
    <NCard title="快捷操作">
      <NSpace>
        <NButton type="primary" @click="goToDishes">管理菜品</NButton>
        <NButton @click="goToRecommend">智能推荐</NButton>
        <NButton @click="goToRecords">用餐记录</NButton>
      </NSpace>
    </NCard>
  </div>
</template>

<style scoped>
.recommend-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.dish-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.dish-card:hover {
  transform: translateY(-2px);
}

.dish-info h3 {
  margin-bottom: 8px;
  font-size: 16px;
}
</style>

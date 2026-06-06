<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NCard, NGrid, NGi, NStatistic, NEmpty } from 'naive-ui'
import { useStatsStore } from '@/stores'

const statsStore = useStatsStore()

onMounted(async () => {
  await statsStore.fetchDashboardStats()
})
</script>

<template>
  <div class="page-container">
    <h1 class="page-title">数据统计</h1>
    
    <NGrid :cols="2" :x-gap="16" :y-gap="16" style="margin-bottom: 24px">
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
    </NGrid>
    
    <!-- 分类分布 -->
    <NCard title="分类分布" style="margin-bottom: 16px">
      <div v-if="statsStore.dashboard?.category_distribution">
        <div v-for="(count, category) in statsStore.dashboard.category_distribution" :key="category" class="stat-item">
          <span>{{ category }}</span>
          <span>{{ count }} 道</span>
        </div>
      </div>
      <NEmpty v-else description="暂无数据" />
    </NCard>
    
    <!-- 热门菜品 -->
    <NCard title="热门菜品">
      <div v-if="statsStore.dashboard?.top_dishes?.length">
        <div v-for="dish in statsStore.dashboard.top_dishes" :key="dish.name" class="stat-item">
          <span>{{ dish.name }}</span>
          <span>{{ dish.count }} 次</span>
        </div>
      </div>
      <NEmpty v-else description="暂无数据" />
    </NCard>
  </div>
</template>

<style scoped>
.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.stat-item:last-child {
  border-bottom: none;
}
</style>

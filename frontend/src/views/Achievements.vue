<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { NCard, NProgress, NSpace, NTag, NEmpty, NSpin, NGrid, NGi, NStatistic, useMessage } from 'naive-ui'
import { achievementApi } from '@/api'
import type { Achievement } from '@/types'

const message = useMessage()
const loading = ref(false)
const achievements = ref<Achievement[]>([])
const progress = ref<Record<string, number>>({})

const unlocked = computed(() => achievements.value.filter(a => a.is_unlocked))
const locked = computed(() => achievements.value.filter(a => !a.is_unlocked))
const totalCount = computed(() => achievements.value.length)
const unlockedCount = computed(() => unlocked.value.length)
const completionRate = computed(() => {
  if (totalCount.value === 0) return 0
  return Math.round((unlockedCount.value / totalCount.value) * 100)
})

// 按 category 分组
const grouped = computed(() => {
  const map = new Map<string, Achievement[]>()
  for (const a of achievements.value) {
    const k = a.category || '其他'
    if (!map.has(k)) map.set(k, [])
    map.get(k)!.push(a)
  }
  return Array.from(map.entries()).map(([category, items]) => ({
    category,
    items: items.sort((a, b) => (a.condition_value || 0) - (b.condition_value || 0))
  }))
})

async function fetchAll() {
  loading.value = true
  try {
    const data = await achievementApi.list()
    achievements.value = data.achievements
    progress.value = data.progress
  } finally {
    loading.value = false
  }
}

async function triggerCheck() {
  try {
    const { newly_unlocked } = await achievementApi.check()
    if (newly_unlocked.length > 0) {
      message.success(`🎉 解锁新成就：${newly_unlocked.map(a => a.name).join('、')}`)
      await fetchAll()
    } else {
      message.info('还没有新成就，继续加油 ✨')
    }
  } catch {
    // 全局拦截器已处理
  }
}

onMounted(fetchAll)
</script>

<template>
  <div class="page-container">
    <h1 class="page-title">成就系统 🏆</h1>

    <NSpace vertical :size="16">
      <!-- 顶部统计 -->
      <NGrid :cols="3" :x-gap="16">
        <NGi>
          <NCard>
            <NStatistic label="已解锁成就" :value="unlockedCount">
              <template #suffix>/ {{ totalCount }}</template>
            </NStatistic>
          </NCard>
        </NGi>
        <NGi>
          <NCard>
            <NStatistic label="完成度" :value="completionRate">
              <template #suffix>%</template>
            </NStatistic>
          </NCard>
        </NGi>
        <NGi>
          <NCard>
            <NSpace vertical :size="4">
              <span class="card-label">总进度</span>
              <NProgress
                type="line"
                :percentage="completionRate"
                :height="14"
                :border-radius="7"
                :show-indicator="false"
                color="#18a058"
              />
            </NSpace>
          </NCard>
        </NGi>
      </NGrid>

      <NSpace justify="end">
        <NButton @click="triggerCheck" :loading="loading">🔍 检查新成就</NButton>
      </NSpace>

      <NSpin :show="loading">
        <NEmpty v-if="totalCount === 0" description="暂无成就定义" />

        <div v-for="group in grouped" :key="group.category">
          <h3 class="group-title">{{ group.category }}</h3>
          <NGrid :cols="3" :x-gap="16" :y-gap="16">
            <NGi v-for="ach in group.items" :key="ach.id">
              <NCard
                class="ach-card"
                :class="{ unlocked: ach.is_unlocked }"
              >
                <div class="ach-header">
                  <div class="ach-icon" :class="{ locked: !ach.is_unlocked }">
                    {{ ach.is_unlocked ? ach.icon : '🔒' }}
                  </div>
                  <div class="ach-meta">
                    <h4>{{ ach.name }}</h4>
                    <NTag v-if="ach.is_unlocked" type="success" size="small">已解锁</NTag>
                    <NTag v-else type="default" size="small">未解锁</NTag>
                  </div>
                </div>
                <p class="ach-desc">{{ ach.description }}</p>
                <div class="ach-progress">
                  <NProgress
                    type="line"
                    :percentage="Math.min(100, Math.round(((ach.current || 0) / (ach.condition_value || 1)) * 100))"
                    :height="8"
                    :border-radius="4"
                    :show-indicator="false"
                    :color="ach.is_unlocked ? '#18a058' : '#2080f0'"
                  />
                  <span class="ach-progress-text">
                    {{ ach.current || 0 }} / {{ ach.condition_value }}
                  </span>
                </div>
              </NCard>
            </NGi>
          </NGrid>
        </div>
      </NSpin>
    </NSpace>
  </div>
</template>

<style scoped>
.card-label {
  font-size: 14px;
  color: #999;
  margin-bottom: 4px;
}

.group-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 16px 0 12px 0;
}

.ach-card {
  transition: transform 0.2s, box-shadow 0.2s;
  height: 100%;
}

.ach-card.unlocked {
  border-color: #18a058;
}

.ach-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.ach-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.ach-icon {
  font-size: 32px;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #d1fae5, #fef3c7);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.ach-icon.locked {
  background: #f5f5f5;
  filter: grayscale(0.5);
}

.ach-meta h4 {
  margin: 0 0 4px 0;
  font-size: 15px;
}

.ach-desc {
  font-size: 13px;
  color: #666;
  margin: 8px 0;
  line-height: 1.5;
}

.ach-progress {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
}

.ach-progress :deep(.n-progress) {
  flex: 1;
}

.ach-progress-text {
  font-size: 12px;
  color: #999;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}
</style>
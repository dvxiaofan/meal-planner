<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { NCard, NEmpty, NList, NListItem, NThing, NTag, NRate, NTabs, NTabPane, NSpin, NButton, NImage } from 'naive-ui'
import { useRecordStore } from '@/stores'
import type { MealRecord } from '@/types'

const recordStore = useRecordStore()
const router = useRouter()
const activeTab = ref('list')
const loading = ref(false)

const photos = computed<MealRecord[]>(() =>
  recordStore.records.filter(r => r.photo_url)
)

onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([
      recordStore.fetchRecords(),
      recordStore.fetchTimeline(100)
    ])
  } finally {
    loading.value = false
  }
})

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

function goToDish(dishId?: number) {
  if (dishId) router.push({ name: 'dish-detail', params: { id: dishId } })
}

// 合并：时间线按日期降序
const recordsByDate = computed(() => {
  const groups = new Map<string, MealRecord[]>()
  for (const r of recordStore.records) {
    const d = r.record_date?.slice(0, 10) || '未知'
    if (!groups.has(d)) groups.set(d, [])
    groups.get(d)!.push(r)
  }
  return Array.from(groups.entries()).sort((a, b) => b[0].localeCompare(a[0]))
})
</script>

<template>
  <div class="page-container">
    <h1 class="page-title">用餐记录</h1>

    <NCard>
      <NTabs v-model:value="activeTab" type="line" animated>
        <NTabPane name="list" tab="📋 列表">
          <NSpin :show="loading">
            <NEmpty v-if="recordStore.records.length === 0" description="暂无用餐记录">
              <template #extra>
                <NButton type="primary" @click="router.push({ name: 'home' })">去首页记录</NButton>
              </template>
            </NEmpty>

            <div v-else>
              <div v-for="[date, items] in recordsByDate" :key="date" class="date-group">
                <h4 class="date-title">{{ date }}</h4>
                <NList>
                  <NListItem v-for="record in items" :key="record.id">
                    <NThing>
                      <template #header>
                        <span class="dish-link" @click="goToDish(record.dish_id)">
                          {{ record.dish?.name || '未知菜品' }}
                        </span>
                      </template>
                      <template #description>
                        <NSpace>
                          <NTag size="small" :type="record.meal_type === 'lunch' ? 'success' : 'info'">
                            {{ record.meal_type === 'lunch' ? '午餐' : '晚餐' }}
                          </NTag>
                          <NRate v-if="record.rating" :value="record.rating" readonly size="small" />
                          <NTag v-if="record.photo_url" size="small" type="warning">📷 有照片</NTag>
                        </NSpace>
                        <p v-if="record.note" class="note">{{ record.note }}</p>
                      </template>
                    </NThing>
                  </NListItem>
                </NList>
              </div>
            </div>
          </NSpin>
        </NTabPane>

        <NTabPane name="photo" tab="📷 照片墙">
          <NSpin :show="loading">
            <NEmpty v-if="photos.length === 0" description="还没有照片记录">
              <template #extra>
                <NButton type="primary" @click="router.push({ name: 'home' })">去添加</NButton>
              </template>
            </NEmpty>

            <div v-else class="masonry">
              <div
                v-for="record in photos"
                :key="record.id"
                class="masonry-item"
                @click="goToDish(record.dish_id)"
              >
                <NImage
                  :src="record.photo_url"
                  :alt="record.dish?.name"
                  object-fit="cover"
                  preview-disabled
                  style="border-radius: 8px 8px 0 0"
                />
                <div class="masonry-meta">
                  <div class="masonry-name">{{ record.dish?.name }}</div>
                  <div class="masonry-date">
                    <NTag size="tiny" :type="record.meal_type === 'lunch' ? 'success' : 'info'">
                      {{ record.meal_type === 'lunch' ? '午' : '晚' }}
                    </NTag>
                    <span>{{ formatDate(record.record_date) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </NSpin>
        </NTabPane>
      </NTabs>
    </NCard>
  </div>
</template>

<style scoped>
.date-group {
  margin-bottom: 24px;
}

.date-title {
  font-size: 14px;
  color: #999;
  margin: 0 0 12px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
}

.dish-link {
  cursor: pointer;
  color: #18a058;
}

.dish-link:hover {
  text-decoration: underline;
}

.note {
  margin-top: 8px;
  color: #666;
  font-size: 13px;
  line-height: 1.5;
}

/* 瀑布流 */
.masonry {
  column-count: 3;
  column-gap: 16px;
}

.masonry-item {
  break-inside: avoid;
  margin-bottom: 16px;
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: transform 0.2s;
  display: inline-block;
  width: 100%;
}

.masonry-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.masonry-meta {
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.masonry-name {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.masonry-date {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #999;
}

@media (max-width: 900px) {
  .masonry {
    column-count: 2;
  }
}

@media (max-width: 540px) {
  .masonry {
    column-count: 1;
  }
}
</style>
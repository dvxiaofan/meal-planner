<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { NCard, NGrid, NGi, NStatistic, NButton, NSpace, NTag, NEmpty, NSpin, NDivider, NIcon, useMessage } from 'naive-ui'
import { CalendarOutline, CheckmarkCircle, FlashOutline, RestaurantOutline } from '@vicons/ionicons5'
import { useStatsStore, useRecommendStore, useRecordStore, useAchievementStore } from '@/stores'
import { usageApi } from '@/api'
import { useDishStore } from '@/stores'
import type { Dish, MealRecord } from '@/types'
import RecordMealModal from '@/components/RecordMealModal.vue'

const router = useRouter()
const message = useMessage()
const statsStore = useStatsStore()
const recommendStore = useRecommendStore()
const recordStore = useRecordStore()
const achievementStore = useAchievementStore()
const dishStore = useDishStore()

const todayRecommend = ref<Dish[]>([])
const loading = ref(false)
const showRecordModal = ref(false)
const recordDish = ref<Dish | null>(null)
const todayStr = new Date().toISOString().slice(0, 10)

function openRecord(dish: Dish) {
  recordDish.value = dish
  showRecordModal.value = true
}

// 7天打卡数据
const streakDays = computed(() => {
  // 用 trend 最后 7 天计算连续打卡
  const series = statsStore.trend || []
  let count = 0
  for (let i = series.length - 1; i >= 0; i--) {
    if (series[i].count > 0) count++
    else break
  }
  return count
})

const weekDays = computed(() => {
  const today = new Date()
  const days = []
  for (let i = 6; i >= 0; i--) {
    const d = new Date(today)
    d.setDate(d.getDate() - i)
    const ds = d.toISOString().slice(0, 10)
    const series = statsStore.trend || []
    const point = series.find(s => s.date === ds)
    const isToday = ds === todayStr
    days.push({
      date: ds,
      dayLabel: ['日', '一', '二', '三', '四', '五', '六'][d.getDay()],
      count: point?.count || 0,
      isToday
    })
  }
  return days
})

// 今日已记录
const todayRecords = computed<MealRecord[]>(() =>
  recordStore.records.filter(r => r.record_date?.slice(0, 10) === todayStr)
)
const hadLunch = computed(() => todayRecords.value.some(r => r.meal_type === 'lunch'))
const hadDinner = computed(() => todayRecords.value.some(r => r.meal_type === 'dinner'))

// 当前时段提醒
const mealHint = computed(() => {
  const h = new Date().getHours()
  if (h < 10) return { text: '🌅 早餐还没吃', need: 'breakfast' as const }
  if (h < 14) return hadLunch.value
    ? { text: '✅ 午餐已记录', need: 'dinner' as const }
    : { text: '🍱 还没记录午餐', need: 'lunch' as const }
  if (h < 17) return hadLunch.value
    ? { text: '⏰ 下午茶时间', need: 'snack' as const }
    : { text: '🍱 还没记录午餐', need: 'lunch' as const }
  if (h < 21) return hadDinner.value
    ? { text: '✅ 晚餐已记录', need: null }
    : { text: '🌙 还没记录晚餐', need: 'dinner' as const }
  return { text: '🌃 夜宵时间', need: 'snack' as const }
})

const unlockedCount = computed(() => {
  return achievementStore.achievements.filter(a => a.is_unlocked).length
})

// 随机挑一道今日推荐菜快捷记录
function quickRecord() {
  if (todayRecommend.value.length === 0) {
    message.warning('暂无推荐菜')
    return
  }
  const dish = todayRecommend.value[Math.floor(Math.random() * todayRecommend.value.length)]
  openRecord(dish)
  usageApi.increment('quick_record').catch(() => {})
}

onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([
      statsStore.fetchDashboardStats(),
      statsStore.fetchTrend(7),
      recommendStore.fetchDailyRecommend('lunch'),
      recordStore.fetchRecords({ limit: 50 }),
      achievementStore.fetchList().catch(() => {}),
      dishStore.dishes.length === 0 ? dishStore.fetchDishes() : Promise.resolve()
    ])
    todayRecommend.value = recommendStore.dailyDishes
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="page-container">
    <h1 class="page-title">欢迎使用食光 🍽️</h1>

    <NSpace vertical :size="20">
      <!-- 顶部统计 -->
      <NGrid :cols="4" :x-gap="16" :y-gap="16">
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
            <NStatistic label="连续打卡" :value="streakDays">
              <template #suffix>天</template>
            </NStatistic>
          </NCard>
        </NGi>
        <NGi>
          <NCard>
            <NStatistic label="成就解锁" :value="unlockedCount" />
          </NCard>
        </NGi>
      </NGrid>

      <!-- 今日摘要 + 快捷记录 -->
      <NCard>
        <NSpace align="center" :wrap="true">
          <div class="hint-text">
            <NIcon :component="FlashOutline" :size="18" style="vertical-align: middle" />
            {{ mealHint.text }}
          </div>
          <NButton type="primary" @click="quickRecord" :disabled="todayRecommend.length === 0">
            <template #icon><NIcon :component="RestaurantOutline" /></template>
            快速记录
          </NButton>
          <NButton @click="router.push({ name: 'dishes' })">管理菜品</NButton>
          <NButton @click="router.push({ name: 'wheel' })">美食转盘</NButton>
          <NButton @click="router.push({ name: 'weekly-plan' })">周计划</NButton>
        </NSpace>
      </NCard>

      <!-- 7 天打卡 -->
      <NCard title="📅 近 7 天打卡" size="small">
        <div class="streak-grid">
          <div
            v-for="day in weekDays"
            :key="day.date"
            class="streak-day"
            :class="{ today: day.isToday, active: day.count > 0 }"
          >
            <div class="day-label">{{ day.dayLabel }}</div>
            <div class="day-date">{{ day.date.slice(5) }}</div>
            <div class="day-status">
              <NIcon
                v-if="day.count > 0"
                :component="CheckmarkCircle"
                :size="20"
                color="#18a058"
              />
              <div v-else class="day-empty">—</div>
            </div>
            <div v-if="day.count > 0" class="day-count">{{ day.count }} 餐</div>
          </div>
        </div>
        <div class="streak-summary">
          <span v-if="streakDays > 0" class="text-success">🔥 已连续打卡 {{ streakDays }} 天</span>
          <span v-else class="text-muted">今天还没有记录，去吃点好的吧</span>
        </div>
      </NCard>

      <!-- 今日推荐 -->
      <NCard title="🌟 今日推荐" size="small">
        <template #header-extra>
          <NButton text type="primary" @click="router.push({ name: 'recommend' })">查看更多</NButton>
        </template>
        <NSpin :show="loading">
          <div v-if="todayRecommend.length > 0" class="recommend-list">
            <NCard v-for="dish in todayRecommend" :key="dish.id" class="dish-card" size="small">
              <div class="dish-info">
                <h4>{{ dish.name }}</h4>
                <NSpace size="small">
                  <NTag v-if="dish.category" size="tiny">{{ dish.category }}</NTag>
                  <NTag v-if="dish.taste" size="tiny" type="info">{{ dish.taste }}</NTag>
                </NSpace>
                <NButton size="tiny" type="primary" block style="margin-top: 8px" @click="openRecord(dish)">
                  记录这餐
                </NButton>
              </div>
            </NCard>
          </div>
          <NEmpty v-else description="暂无推荐" />
        </NSpin>
      </NCard>

      <!-- 今日餐别状态 -->
      <NCard title="🍽️ 今日餐别" size="small">
        <NSpace>
          <NTag :type="hadLunch ? 'success' : 'default'" size="large" round>
            {{ hadLunch ? '✅' : '⬜' }} 午餐
          </NTag>
          <NTag :type="hadDinner ? 'success' : 'default'" size="large" round>
            {{ hadDinner ? '✅' : '⬜' }} 晚餐
          </NTag>
        </NSpace>
      </NCard>
    </NSpace>

    <RecordMealModal v-model:show="showRecordModal" :dish="recordDish" />
  </div>
</template>

<style scoped>
.hint-text {
  font-size: 15px;
  color: #333;
  font-weight: 500;
}

.streak-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 8px;
  margin-bottom: 12px;
}

.streak-day {
  text-align: center;
  padding: 8px 4px;
  border-radius: 8px;
  background: #fafafa;
  border: 1px solid transparent;
  transition: all 0.2s;
}

.streak-day.active {
  background: #f0fdf4;
  border-color: #bbf7d0;
}

.streak-day.today {
  border-color: #18a058;
  box-shadow: 0 0 0 2px rgba(24, 160, 88, 0.15);
}

.day-label {
  font-size: 12px;
  color: #999;
}

.day-date {
  font-size: 11px;
  color: #bbb;
  margin: 2px 0 4px 0;
}

.day-empty {
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ddd;
}

.day-count {
  font-size: 11px;
  color: #18a058;
  margin-top: 2px;
}

.streak-summary {
  text-align: center;
  font-size: 13px;
}

.text-success { color: #18a058; }
.text-muted { color: #999; }

.recommend-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
}

.dish-card {
  transition: transform 0.2s;
}

.dish-card:hover {
  transform: translateY(-2px);
}

.dish-info h4 {
  margin: 0 0 6px 0;
  font-size: 15px;
}

@media (max-width: 640px) {
  .streak-grid {
    gap: 4px;
  }
  .day-label, .day-date, .day-count {
    font-size: 10px;
  }
}
</style>
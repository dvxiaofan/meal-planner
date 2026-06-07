<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  NCard, NButton, NSpace, NTag, NEmpty, NSpin, NModal, NList, NListItem, NThing, NRate, useMessage
} from 'naive-ui'
import { useRecordStore } from '@/stores'
import type { MealRecord } from '@/types'

const router = useRouter()
const message = useMessage()
const recordStore = useRecordStore()

const loading = ref(false)
const currentMonth = ref(new Date())
const showDayModal = ref(false)
const selectedDay = ref<string | null>(null)

const weekdays = ['日', '一', '二', '三', '四', '五', '六']

// 当前月份的网格（6 行 × 7 列）
const monthGrid = computed(() => {
  const year = currentMonth.value.getFullYear()
  const month = currentMonth.value.getMonth()
  // 本月第一天
  const firstDay = new Date(year, month, 1)
  const firstWeekday = firstDay.getDay()  // 0=Sun
  // 本月天数
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  // 上月填充
  const prevMonthLast = new Date(year, month, 0).getDate()
  const cells: Array<{ date: string; day: number; isCurrentMonth: boolean; isToday: boolean; records: MealRecord[] }> = []
  const todayStr = new Date().toISOString().slice(0, 10)
  // 前面填充上个月
  for (let i = firstWeekday - 1; i >= 0; i--) {
    const d = new Date(year, month - 1, prevMonthLast - i)
    const ds = d.toISOString().slice(0, 10)
    cells.push({ date: ds, day: prevMonthLast - i, isCurrentMonth: false, isToday: false, records: [] })
  }
  // 本月
  for (let day = 1; day <= daysInMonth; day++) {
    const d = new Date(year, month, day)
    const ds = d.toISOString().slice(0, 10)
    cells.push({
      date: ds,
      day,
      isCurrentMonth: true,
      isToday: ds === todayStr,
      records: []
    })
  }
  // 后面填充下个月直到 42 格
  let nextDay = 1
  while (cells.length < 42) {
    const d = new Date(year, month + 1, nextDay)
    const ds = d.toISOString().slice(0, 10)
    cells.push({ date: ds, day: nextDay, isCurrentMonth: false, isToday: false, records: [] })
    nextDay++
  }
  return cells
})

// 用 records 填充
const filledGrid = computed(() => {
  const recordsByDate = new Map<string, MealRecord[]>()
  for (const r of recordStore.records) {
    const d = r.record_date?.slice(0, 10)
    if (!d) continue
    if (!recordsByDate.has(d)) recordsByDate.set(d, [])
    recordsByDate.get(d)!.push(r)
  }
  return monthGrid.value.map(cell => ({
    ...cell,
    records: recordsByDate.get(cell.date) || []
  }))
})

const monthLabel = computed(() => {
  return `${currentMonth.value.getFullYear()} 年 ${currentMonth.value.getMonth() + 1} 月`
})

const monthStats = computed(() => {
  const current = filledGrid.value.filter(c => c.isCurrentMonth)
  const totalRecords = current.reduce((s, c) => s + c.records.length, 0)
  const daysWithRecords = current.filter(c => c.records.length > 0).length
  return { totalRecords, daysWithRecords, days: current.length }
})

function shiftMonth(delta: number) {
  const d = new Date(currentMonth.value)
  d.setMonth(d.getMonth() + delta)
  currentMonth.value = d
}

function goToday() {
  currentMonth.value = new Date()
}

function openDay(date: string, records: MealRecord[]) {
  if (records.length === 0) return
  selectedDay.value = date
  showDayModal.value = true
}

function viewDish(dishId?: number) {
  if (dishId) router.push({ name: 'dish-detail', params: { id: dishId } })
}

onMounted(async () => {
  loading.value = true
  try {
    if (recordStore.records.length === 0) {
      await recordStore.fetchRecords({ limit: 200 })
    }
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="page-container">
    <h1 class="page-title">餐日历 📅</h1>

    <NCard>
      <!-- 头部 -->
      <div class="header-bar">
        <NSpace align="center">
          <NButton @click="shiftMonth(-1)">‹ 上月</NButton>
          <NButton @click="goToday">今天</NButton>
          <NButton @click="shiftMonth(1)">下月 ›</NButton>
          <span class="month-label">{{ monthLabel }}</span>
        </NSpace>
        <NSpace>
          <NTag type="info">本月 {{ monthStats.totalRecords }} 餐</NTag>
          <NTag type="success">打卡 {{ monthStats.daysWithRecords }} / {{ monthStats.days }} 天</NTag>
        </NSpace>
      </div>

      <NSpin :show="loading">
        <div class="calendar">
          <!-- 星期表头 -->
          <div
            v-for="(w, i) in weekdays"
            :key="`w-${i}`"
            class="cal-header"
            :class="{ weekend: i === 0 || i === 6 }"
          >
            {{ w }}
          </div>

          <!-- 日期格子 -->
          <div
            v-for="cell in filledGrid"
            :key="cell.date"
            class="cal-cell"
            :class="{
              'other-month': !cell.isCurrentMonth,
              'today': cell.isToday,
              'has-records': cell.records.length > 0
            }"
            @click="openDay(cell.date, cell.records)"
          >
            <div class="cal-day">{{ cell.day }}</div>
            <div v-if="cell.records.length > 0" class="cal-dots">
              <span
                v-for="r in cell.records"
                :key="r.id"
                class="cal-dot"
                :class="r.meal_type"
                :title="`${r.meal_type === 'lunch' ? '午' : '晚'}: ${r.dish?.name}`"
              />
            </div>
          </div>
        </div>
      </NSpin>

      <!-- 图例 -->
      <div class="legend">
        <NSpace>
          <span class="legend-item">
            <span class="cal-dot lunch"></span> 午餐
          </span>
          <span class="legend-item">
            <span class="cal-dot dinner"></span> 晚餐
          </span>
          <span class="legend-item text-muted">点击有餐的日期查看详情</span>
        </NSpace>
      </div>
    </NCard>

    <!-- 某天详情 -->
    <NModal
      v-model:show="showDayModal"
      preset="card"
      :title="selectedDay || ''"
      style="width: 520px; max-width: 95vw"
    >
      <NList v-if="selectedDay">
        <NListItem
          v-for="r in recordStore.records.filter(x => x.record_date?.slice(0, 10) === selectedDay)"
          :key="r.id"
        >
          <NThing>
            <template #header>
              <span class="dish-link" @click="viewDish(r.dish_id)">
                {{ r.dish?.name || '未知菜品' }}
              </span>
            </template>
            <template #description>
              <NSpace>
                <NTag size="small" :type="r.meal_type === 'lunch' ? 'success' : 'info'">
                  {{ r.meal_type === 'lunch' ? '午餐' : '晚餐' }}
                </NTag>
                <NRate v-if="r.rating" :value="r.rating" readonly size="small" />
              </NSpace>
              <p v-if="r.note" class="note">{{ r.note }}</p>
            </template>
          </NThing>
        </NListItem>
      </NList>
    </NModal>
  </div>
</template>

<style scoped>
.header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}

.month-label {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  min-width: 140px;
  text-align: center;
}

.calendar {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.cal-header {
  text-align: center;
  font-size: 13px;
  font-weight: 500;
  color: #999;
  padding: 8px 0;
  background: #fafafa;
  border-radius: 4px;
}

.cal-header.weekend {
  color: #f0a020;
}

.cal-cell {
  aspect-ratio: 1;
  padding: 6px;
  background: #fff;
  border: 1px solid #f0f0f0;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  transition: all 0.2s;
  min-height: 60px;
}

.cal-cell:hover {
  border-color: #18a058;
  box-shadow: 0 2px 8px rgba(24, 160, 88, 0.1);
}

.cal-cell.other-month {
  opacity: 0.4;
}

.cal-cell.today {
  border-color: #18a058;
  background: #f0fdf4;
  box-shadow: 0 0 0 2px rgba(24, 160, 88, 0.2);
}

.cal-cell.has-records {
  background: #fffbeb;
}

.cal-cell.has-records.today {
  background: #f0fdf4;
}

.cal-day {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.cal-cell.today .cal-day {
  color: #18a058;
  font-weight: 700;
}

.cal-dots {
  display: flex;
  gap: 3px;
  margin-top: 4px;
  flex-wrap: wrap;
  justify-content: center;
}

.cal-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.cal-dot.lunch { background: #18a058; }
.cal-dot.dinner { background: #2080f0; }

.legend {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
  font-size: 12px;
  color: #999;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.text-muted { color: #bbb; }

.dish-link {
  cursor: pointer;
  color: #18a058;
}

.dish-link:hover {
  text-decoration: underline;
}

.note {
  margin-top: 4px;
  color: #666;
  font-size: 12px;
}

@media (max-width: 640px) {
  .cal-cell {
    min-height: 50px;
    padding: 4px 2px;
  }
  .cal-day { font-size: 12px; }
  .cal-dot { width: 6px; height: 6px; }
}
</style>
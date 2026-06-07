<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  NCard, NButton, NSpace, NTag, NEmpty, NSpin, NTabs, NTabPane,
  NPopconfirm, NSelect, NGrid, NGi, NDivider, NModal, useMessage
} from 'naive-ui'
import draggable from 'vuedraggable'
import { weeklyPlanApi, dishApi, pantryApi } from '@/api'
import type { WeeklyPlanItem, Dish, ShoppingListResponse } from '@/types'
import { useDishStore } from '@/stores'
import RecordMealModal from '@/components/RecordMealModal.vue'

const router = useRouter()
const message = useMessage()
const dishStore = useDishStore()

const loading = ref(false)
const activeTab = ref('plan')
const weekStart = ref(getMonday(new Date()))
const items = ref<WeeklyPlanItem[]>([])
const shoppingList = ref<ShoppingListResponse | null>(null)
const showSwapModal = ref(false)
const importing = ref(false)
const swapTarget = ref<WeeklyPlanItem | null>(null)
const swapDishId = ref<number | null>(null)
const showRecordModal = ref(false)
const recordDish = ref<Dish | null>(null)

const dayLabels = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
const dayShortLabels = ['一', '二', '三', '四', '五', '六', '日']

function getMonday(d: Date): string {
  const dt = new Date(d)
  const day = dt.getDay()
  const diff = day === 0 ? -6 : 1 - day
  dt.setDate(dt.getDate() + diff)
  return dt.toISOString().slice(0, 10)
}

function shiftWeek(delta: number) {
  const d = new Date(weekStart.value)
  d.setDate(d.getDate() + delta * 7)
  weekStart.value = getMonday(d)
  fetchAll()
}

const weekRange = computed(() => {
  const start = new Date(weekStart.value)
  const end = new Date(start)
  end.setDate(end.getDate() + 6)
  return `${start.getMonth() + 1}/${start.getDate()} - ${end.getMonth() + 1}/${end.getDate()}`
})

const isCurrentWeek = computed(() => {
  return weekStart.value === getMonday(new Date())
})

// 索引化：plan[day][mealType]
const planMap = computed(() => {
  const map: Record<number, { lunch?: WeeklyPlanItem; dinner?: WeeklyPlanItem }> = {}
  for (let d = 1; d <= 7; d++) map[d] = {}
  for (const it of items.value) {
    if (it.meal_type === 'lunch' || it.meal_type === 'dinner') {
      map[it.day_of_week][it.meal_type] = it
    }
  }
  return map
})

// 拖拽用：每行 7 个槽位
const lunchSlots = computed(() => {
  return Array.from({ length: 7 }, (_, i) => planMap.value[i + 1].lunch || null)
})
const dinnerSlots = computed(() => {
  return Array.from({ length: 7 }, (_, i) => planMap.value[i + 1].dinner || null)
})

const dishOptions = computed(() =>
  dishStore.dishes
    .filter(d => d.is_enabled)
    .map(d => ({ label: `${d.name}${d.is_favorite ? ' ★' : ''}`, value: d.id }))
)

const totalMeals = computed(() => items.value.length)

const groupedShopping = computed(() => {
  if (!shoppingList.value) return []
  return Object.entries(shoppingList.value.by_category).map(([cat, list]) => ({ cat, list }))
})

async function fetchAll() {
  loading.value = true
  try {
    const [plan, list] = await Promise.all([
      weeklyPlanApi.get(weekStart.value),
      activeTab.value === 'shopping' ? weeklyPlanApi.shoppingList(weekStart.value) : Promise.resolve(null)
    ])
    items.value = plan.items
    if (list) shoppingList.value = list
  } finally {
    loading.value = false
  }
}

async function fetchShopping() {
  try {
    shoppingList.value = await weeklyPlanApi.shoppingList(weekStart.value)
  } catch {
    // 拦截器处理
  }
}

async function generatePlan() {
  loading.value = true
  try {
    const data = await weeklyPlanApi.generate({ week_start: weekStart.value, replace: true })
    items.value = data.items
    message.success(`已生成 ${data.items.length} 个餐位`)
    if (activeTab.value === 'shopping') await fetchShopping()
  } catch {
    // 拦截器处理
  } finally {
    loading.value = false
  }
}

function openSwap(item: WeeklyPlanItem) {
  swapTarget.value = item
  swapDishId.value = item.dish?.id ?? null
  showSwapModal.value = true
}

async function confirmSwap() {
  if (!swapTarget.value || !swapDishId.value) return
  try {
    const updated = await weeklyPlanApi.swap(swapTarget.value.id, swapDishId.value)
    const idx = items.value.findIndex(i => i.id === updated.id)
    if (idx >= 0) items.value[idx] = updated
    showSwapModal.value = false
    message.success('已换菜')
  } catch {
    // 拦截器处理
  }
}

async function removeMeal(item: WeeklyPlanItem) {
  try {
    await weeklyPlanApi.remove(item.id)
    items.value = items.value.filter(i => i.id !== item.id)
    message.success('已删除')
  } catch {
    // 拦截器处理
  }
}

interface SlotPayload {
  newIndex: number
  oldIndex: number
  item: WeeklyPlanItem
  from: 'lunch' | 'dinner'
  to: 'lunch' | 'dinner'
}

async function onDragChange(evt: any, row: 'lunch' | 'dinner') {
  // vuedraggable @change 事件：added / removed / moved
  if (evt.added) {
    const moved = evt.added.element as WeeklyPlanItem
    const newIndex = evt.added.newIndex
    // 新目标位置上的原 item（如果存在）
    const targetItem = (row === 'lunch' ? lunchSlots : dinnerSlots).value[newIndex]
    if (targetItem && targetItem.id !== moved.id) {
      try {
        const { items: updated } = await weeklyPlanApi.swapPositions(moved.id, targetItem.id)
        for (const u of updated) {
          const i = items.value.findIndex(x => x.id === u.id)
          if (i >= 0) items.value[i] = u
        }
      } catch {
        // 拦截器处理
      }
    } else {
      // 目标位置为空：直接更新本地状态
      const i = items.value.findIndex(x => x.id === moved.id)
      if (i >= 0) {
        items.value[i] = {
          ...items.value[i],
          day_of_week: newIndex + 1,
          meal_type: row
        }
      }
    }
  } else if (evt.moved) {
    // 同行内调换：直接更新 day_of_week
    const moved = evt.moved.element as WeeklyPlanItem
    const newIndex = evt.moved.newIndex
    const i = items.value.findIndex(x => x.id === moved.id)
    if (i >= 0) {
      items.value[i] = { ...items.value[i], day_of_week: newIndex + 1 }
    }
  }
}

function goToDish(dish: Dish | null) {
  if (dish) router.push({ name: 'dish-detail', params: { id: dish.id } })
}

function openRecord(dish: Dish) {
  recordDish.value = dish
  showRecordModal.value = true
}

async function handleTabChange(name: string | number) {
  if (name === 'shopping' && !shoppingList.value) {
    await fetchShopping()
  }
}

async function importAllToPantry() {
  if (!shoppingList.value) return
  importing.value = true
  try {
    const items = shoppingList.value.items.map(it => ({
      name: it.name,
      amount: it.amounts[0] || undefined,
      category: it.type || undefined
    }))
    const { count } = await pantryApi.addFromShoppingList(items)
    message.success(`已加入 ${count} 项到库存`)
  } catch {
    // 拦截器处理
  } finally {
    importing.value = false
  }
}

onMounted(async () => {
  if (dishStore.dishes.length === 0) {
    await dishStore.fetchDishes()
  }
  await fetchAll()
})
</script>

<template>
  <div class="page-container">
    <h1 class="page-title">周计划 📅</h1>

    <NCard>
      <!-- 头部：周导航 + 操作 -->
      <div class="header-bar">
        <NSpace align="center">
          <NButton @click="shiftWeek(-1)">‹ 上一周</NButton>
          <NButton @click="shiftWeek(0)" :type="isCurrentWeek ? 'primary' : 'default'">本周</NButton>
          <NButton @click="shiftWeek(1)">下一周 ›</NButton>
          <span class="week-range">{{ weekRange }}<NTag v-if="isCurrentWeek" type="success" size="small" style="margin-left: 8px">本周</NTag></span>
        </NSpace>
        <NSpace>
          <NTag type="info" size="small">已规划 {{ totalMeals }} / 14 餐</NTag>
          <NButton type="primary" @click="generatePlan">✨ 一键生成本周</NButton>
        </NSpace>
      </div>

      <NDivider />

      <NTabs v-model:value="activeTab" type="line" animated @update:value="handleTabChange">
        <!-- 计划视图 -->
        <NTabPane name="plan" tab="📅 计划">
          <NSpin :show="loading">
            <NEmpty v-if="items.length === 0" description="本周还没规划菜单">
              <template #extra>
                <NButton type="primary" @click="generatePlan">一键生成本周</NButton>
              </template>
            </NEmpty>

            <div v-else class="plan-grid">
              <div class="grid-header"></div>
              <div v-for="(label, idx) in dayLabels" :key="idx" class="day-header">
                {{ label }}
                <div class="day-date">{{ new Date(new Date(weekStart).getTime() + idx * 86400000).getDate() }}</div>
              </div>

              <div class="meal-label">午餐</div>
              <draggable
                v-model="lunchSlots"
                group="meals"
                item-key="id"
                class="meal-row"
                :animation="200"
                ghost-class="dragging-ghost"
                @change="(e: any) => onDragChange(e, 'lunch')"
              >
                <template #item="{ element, index }">
                  <div class="meal-cell" :key="element?.id || `l-empty-${index}`">
                    <NCard v-if="element" size="small" class="meal-card" hoverable>
                      <div class="meal-card-content" @click="goToDish(element.dish)">
                        <div class="meal-emoji" v-if="!element.dish?.image_url">🍽️</div>
                        <img v-else :src="element.dish!.image_url" class="meal-img" />
                        <div class="meal-name">{{ element.dish?.name }}</div>
                        <NTag v-if="element.dish?.taste" size="tiny" type="info">
                          {{ element.dish?.taste }}
                        </NTag>
                      </div>
                      <template #action>
                        <NSpace size="small">
                          <NButton size="tiny" @click="openSwap(element)">换菜</NButton>
                          <NPopconfirm @positive-click="removeMeal(element)">
                            <template #trigger>
                              <NButton size="tiny" type="error" ghost>删除</NButton>
                            </template>
                            删除这餐？
                          </NPopconfirm>
                          <NButton
                            v-if="element.dish"
                            size="tiny"
                            type="primary"
                            ghost
                            @click="openRecord(element.dish!)"
                          >记录</NButton>
                        </NSpace>
                      </template>
                    </NCard>
                    <div v-else class="meal-empty">
                      <NButton size="small" dashed @click="generatePlan">未规划</NButton>
                    </div>
                  </div>
                </template>
              </draggable>

              <div class="meal-label">晚餐</div>
              <draggable
                v-model="dinnerSlots"
                group="meals"
                item-key="id"
                class="meal-row"
                :animation="200"
                ghost-class="dragging-ghost"
                @change="(e: any) => onDragChange(e, 'dinner')"
              >
                <template #item="{ element, index }">
                  <div class="meal-cell" :key="element?.id || `d-empty-${index}`">
                    <NCard v-if="element" size="small" class="meal-card" hoverable>
                      <div class="meal-card-content" @click="goToDish(element.dish)">
                        <div class="meal-emoji" v-if="!element.dish?.image_url">🌙</div>
                        <img v-else :src="element.dish!.image_url" class="meal-img" />
                        <div class="meal-name">{{ element.dish?.name }}</div>
                        <NTag v-if="element.dish?.taste" size="tiny" type="info">
                          {{ element.dish?.taste }}
                        </NTag>
                      </div>
                      <template #action>
                        <NSpace size="small">
                          <NButton size="tiny" @click="openSwap(element)">换菜</NButton>
                          <NPopconfirm @positive-click="removeMeal(element)">
                            <template #trigger>
                              <NButton size="tiny" type="error" ghost>删除</NButton>
                            </template>
                            删除这餐？
                          </NPopconfirm>
                          <NButton
                            v-if="element.dish"
                            size="tiny"
                            type="primary"
                            ghost
                            @click="openRecord(element.dish!)"
                          >记录</NButton>
                        </NSpace>
                      </template>
                    </NCard>
                    <div v-else class="meal-empty">
                      <NButton size="small" dashed @click="generatePlan">未规划</NButton>
                    </div>
                  </div>
                </template>
              </draggable>
            </div>
          </NSpin>
        </NTabPane>

        <!-- 购物清单 -->
        <NTabPane name="shopping" tab="🛒 购物清单">
          <NSpin :show="loading">
            <NEmpty v-if="!shoppingList || shoppingList.items.length === 0" description="暂无购物清单">
              <template #extra>
                <NButton type="primary" @click="generatePlan">先生成周计划</NButton>
              </template>
            </NEmpty>

            <div v-else>
              <NSpace style="margin-bottom: 16px" align="center" :wrap="true">
                <NTag type="info">📅 {{ shoppingList.week_start }} 周</NTag>
                <NTag>共 {{ shoppingList.items.length }} 种食材</NTag>
                <NButton
                  type="primary"
                  size="small"
                  :loading="importing"
                  @click="importAllToPantry"
                >
                  🧊 全部加入库存
                </NButton>
              </NSpace>

              <div v-for="group in groupedShopping" :key="group.cat" class="shopping-group">
                <h4 class="group-title">
                  <NTag :type="group.cat === '主料' ? 'success' : 'warning'" size="small">{{ group.cat }}</NTag>
                  {{ group.cat }}
                </h4>
                <NGrid :cols="3" :x-gap="12" :y-gap="12">
                  <NGi v-for="item in group.list" :key="item.name">
                    <div class="shopping-item">
                      <div class="item-name">{{ item.name }}</div>
                      <div class="item-meta">
                        <span v-if="item.amounts.length">{{ item.amounts.join(' + ') }}</span>
                        <span v-else class="text-muted">用量未填</span>
                      </div>
                      <div class="item-used">用于：{{ item.used_in.join('、') }}</div>
                    </div>
                  </NGi>
                </NGrid>
              </div>
            </div>
          </NSpin>
        </NTabPane>
      </NTabs>
    </NCard>

    <!-- 换菜弹窗 -->
    <NModal
      v-model:show="showSwapModal"
      preset="card"
      title="换一道菜"
      style="width: 480px; max-width: 95vw"
    >
      <NSpace vertical>
        <div>当前：<strong>{{ swapTarget?.dish?.name }}</strong></div>
        <NSelect
          v-model:value="swapDishId"
          :options="dishOptions"
          filterable
          placeholder="选择新菜品"
          size="large"
        />
        <NSpace justify="end">
          <NButton @click="showSwapModal = false">取消</NButton>
          <NButton type="primary" :disabled="!swapDishId" @click="confirmSwap">确定</NButton>
        </NSpace>
      </NSpace>
    </NModal>

    <RecordMealModal v-model:show="showRecordModal" :dish="recordDish" />
  </div>
</template>

<style scoped>
.header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.week-range {
  font-size: 14px;
  color: #666;
}

.plan-grid {
  display: grid;
  grid-template-columns: 60px repeat(7, 1fr);
  gap: 8px;
  align-items: start;
}

.meal-row {
  display: contents;
}

.dragging-ghost {
  opacity: 0.4;
  background: #f0fdf4;
  border: 2px dashed #18a058;
}

.grid-header {
  /* 左上角空白 */
}

.day-header {
  text-align: center;
  font-size: 13px;
  font-weight: 600;
  color: #333;
  padding: 8px 0;
  background: #f9fafb;
  border-radius: 6px;
}

.day-date {
  font-size: 11px;
  color: #999;
  font-weight: 400;
  margin-top: 2px;
}

.meal-label {
  font-size: 13px;
  color: #666;
  text-align: right;
  padding: 12px 8px 0 0;
  font-weight: 500;
}

.meal-cell {
  min-height: 120px;
}

.meal-card {
  height: 100%;
}

.meal-card-content {
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.meal-emoji {
  font-size: 32px;
}

.meal-img {
  width: 100%;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
}

.meal-name {
  font-size: 13px;
  font-weight: 500;
  text-align: center;
  color: #333;
}

.meal-empty {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 120px;
  border: 1px dashed #e5e7eb;
  border-radius: 6px;
}

.shopping-group {
  margin-bottom: 24px;
}

.group-title {
  font-size: 15px;
  margin: 0 0 12px 0;
  color: #333;
  display: flex;
  align-items: center;
  gap: 8px;
}

.shopping-item {
  background: #fff;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  padding: 10px 12px;
}

.item-name {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.item-meta {
  font-size: 12px;
  color: #666;
}

.text-muted {
  color: #bbb;
}

.item-used {
  font-size: 11px;
  color: #999;
  margin-top: 4px;
  font-style: italic;
}

@media (max-width: 900px) {
  .plan-grid {
    grid-template-columns: 50px repeat(7, 1fr);
    gap: 4px;
  }
  .meal-name {
    font-size: 12px;
  }
  .day-header {
    font-size: 11px;
    padding: 4px 0;
  }
}
</style>
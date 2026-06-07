<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  NCard, NButton, NSpace, NTag, NEmpty, NRadioGroup, NRadioButton,
  NInput, NSpin, NIcon, NTag as NTagComp, NDivider, useMessage
} from 'naive-ui'
import { SparklesOutline, FlashOutline } from '@vicons/ionicons5'
import { useRecommendStore } from '@/stores'
import { aiApi } from '@/api'
import type { Dish } from '@/types'
import RecordMealModal from '@/components/RecordMealModal.vue'

const recommendStore = useRecommendStore()
const message = useMessage()

const mealType = ref('lunch')
const mood = ref('happy')
const recommendDishes = ref<Dish[]>([])

const showRecordModal = ref(false)
const recordDish = ref<Dish | null>(null)

// 智能匹配
const aiQuery = ref('')
const aiLoading = ref(false)
const aiResult = ref<{
  query: string
  preferences: { taste: string[]; category: string[]; ingredients: string[]; difficulty: number[]; max_time: number | null }
  excludes: string[]
  items: Array<{ dish: Dish; score: number; reasons: string[] }>
} | null>(null)

const EXAMPLES = [
  '今天想吃点辣的',
  '清淡的汤',
  '简单的素菜',
  '有鸡蛋 不要辣',
  '快手菜 10分钟搞定',
  '想吃面 不太辣'
]

function openRecord(dish: Dish) {
  recordDish.value = dish
  showRecordModal.value = true
}

const moodOptions = [
  { label: '😊 开心', value: 'happy' },
  { label: '😫 疲惫', value: 'tired' },
  { label: '😴 想偷懒', value: 'lazy' },
  { label: '🌶️ 想吃辣', value: 'spicy' },
  { label: '🥗 想养生', value: 'healthy' }
]

onMounted(async () => {
  await fetchDailyRecommend()
})

async function fetchDailyRecommend() {
  try {
    const dishes = await recommendStore.fetchDailyRecommend(mealType.value)
    recommendDishes.value = dishes
  } catch (error) {
    console.error('获取推荐失败:', error)
  }
}

async function fetchMoodRecommend() {
  try {
    const dishes = await recommendStore.fetchMoodRecommend(mood.value)
    recommendDishes.value = dishes
  } catch (error) {
    console.error('获取心情推荐失败:', error)
  }
}

async function runAiSuggest(query?: string) {
  const q = (query ?? aiQuery.value).trim()
  if (!q) {
    message.warning('请输入想吃什么')
    return
  }
  aiLoading.value = true
  if (query) aiQuery.value = query  // 例子点击时同步
  try {
    aiResult.value = await aiApi.suggest(q, 5)
  } catch {
    // 拦截器处理
  } finally {
    aiLoading.value = false
  }
}
</script>

<template>
  <div class="page-container">
    <h1 class="page-title">智能推荐</h1>

    <!-- 智能匹配（无需 LLM） -->
    <NCard style="margin-bottom: 16px" class="ai-card">
      <template #header>
        <NSpace align="center">
          <NIcon :component="SparklesOutline" :size="20" color="#18a058" />
          <span>智能匹配</span>
          <NTagComp size="tiny" type="success" :bordered="false">免 LLM</NTagComp>
        </NSpace>
      </template>
      <template #header-extra>
        <NTagComp size="small" :bordered="false">试试："今天想吃点辣的" / "清淡的汤" / "有鸡蛋 不要辣"</NTagComp>
      </template>

      <NSpace vertical>
        <NSpace :wrap="true">
          <NButton
            v-for="ex in EXAMPLES"
            :key="ex"
            size="tiny"
            round
            @click="runAiSuggest(ex)"
          >
            {{ ex }}
          </NButton>
        </NSpace>
        <NSpace>
          <NInput
            v-model:value="aiQuery"
            placeholder="告诉我想吃什么（支持口味/食材/难度/时间）"
            style="width: 360px"
            @keyup.enter="runAiSuggest()"
          />
          <NButton type="primary" :loading="aiLoading" @click="runAiSuggest()">
            <template #icon><NIcon :component="FlashOutline" /></template>
            智能匹配
          </NButton>
        </NSpace>

        <!-- 解析出的偏好 -->
        <div v-if="aiResult && (aiResult.preferences.taste.length + aiResult.preferences.category.length + aiResult.preferences.ingredients.length > 0)" class="pref-chips">
          <span class="pref-label">🔍 解析：</span>
          <NTagComp v-for="t in aiResult.preferences.taste" :key="`t-${t}`" size="small" type="error">{{ t }}</NTagComp>
          <NTagComp v-for="c in aiResult.preferences.category" :key="`c-${c}`" size="small" type="success">{{ c }}</NTagComp>
          <NTagComp v-for="i in aiResult.preferences.ingredients" :key="`i-${i}`" size="small" type="info">含 {{ i }}</NTagComp>
          <NTagComp v-if="aiResult.preferences.max_time" size="small" type="warning">≤ {{ aiResult.preferences.max_time }} 分钟</NTagComp>
          <NTagComp v-for="d in aiResult.preferences.difficulty" :key="`d-${d}`" size="small">难度 {{ d }} 星</NTagComp>
        </div>

        <NSpin :show="aiLoading">
          <div v-if="aiResult && aiResult.items.length > 0" class="ai-grid">
            <NCard
              v-for="(item, idx) in aiResult.items"
              :key="item.dish.id"
              class="ai-item"
              :class="{ top: idx === 0 }"
            >
              <div class="ai-rank">#{{ idx + 1 }}</div>
              <div class="ai-image" v-if="item.dish.image_url">
                <img :src="item.dish.image_url" :alt="item.dish.name" />
              </div>
              <div class="ai-image placeholder" v-else>🍽️</div>
              <h4 class="ai-name" @click="openRecord(item.dish)">{{ item.dish.name }}</h4>
              <NSpace size="small">
                <NTag v-if="item.dish.category" size="tiny">{{ item.dish.category }}</NTag>
                <NTag v-if="item.dish.taste" size="tiny" type="info">{{ item.dish.taste }}</NTag>
                <NTag size="tiny" type="warning">⭐ {{ item.dish.difficulty }}</NTag>
                <NTag v-if="item.dish.cook_time" size="tiny">⏱ {{ item.dish.cook_time }}分</NTag>
              </NSpace>
              <div v-if="item.reasons.length" class="ai-reasons">
                <NTag v-for="r in item.reasons" :key="r" size="tiny" :bordered="false" type="success">{{ r }}</NTag>
              </div>
              <NButton size="small" type="primary" block style="margin-top: 8px" @click="openRecord(item.dish)">
                记录这餐
              </NButton>
            </NCard>
          </div>
          <NEmpty
            v-else-if="aiResult && aiResult.items.length === 0 && !aiLoading"
            description="没找到完全匹配的菜，换个描述试试"
          />
        </NSpin>
      </NSpace>
    </NCard>

    <!-- 每日推荐 -->
    <NCard title="每日推荐" style="margin-bottom: 16px">
      <template #header-extra>
        <NRadioGroup v-model:value="mealType" @update:value="fetchDailyRecommend">
          <NRadioButton value="lunch">午餐</NRadioButton>
          <NRadioButton value="dinner">晚餐</NRadioButton>
        </NRadioGroup>
      </template>

      <div v-if="recommendDishes.length > 0" class="recommend-grid">
        <NCard v-for="dish in recommendDishes" :key="dish.id" class="dish-card">
          <div class="dish-image" v-if="dish.image_url">
            <img :src="dish.image_url" :alt="dish.name" />
          </div>
          <div class="dish-image placeholder" v-else>
            🍽️
          </div>
          <div class="dish-info">
            <h3>{{ dish.name }}</h3>
            <NSpace>
              <NTag v-if="dish.category" size="small">{{ dish.category }}</NTag>
              <NTag v-if="dish.taste" size="small" type="info">{{ dish.taste }}</NTag>
            </NSpace>
            <div class="card-actions">
              <NButton size="small" type="primary" @click="openRecord(dish)">
                记录这餐
              </NButton>
            </div>
          </div>
        </NCard>
      </div>
      <NEmpty v-else description="暂无推荐" />

      <template #action>
        <NButton @click="fetchDailyRecommend">换一批</NButton>
      </template>
    </NCard>

    <!-- 心情推荐 -->
    <NCard title="心情推荐">
      <NSpace vertical>
        <NRadioGroup v-model:value="mood">
          <NSpace>
            <NRadioButton
              v-for="option in moodOptions"
              :key="option.value"
              :value="option.value"
            >
              {{ option.label }}
            </NRadioButton>
          </NSpace>
        </NRadioGroup>

        <NButton type="primary" @click="fetchMoodRecommend">根据心情推荐</NButton>
      </NSpace>
    </NCard>

    <RecordMealModal
      v-model:show="showRecordModal"
      :dish="recordDish"
    />
  </div>
</template>

<style scoped>
.ai-card {
  background: linear-gradient(135deg, #f0fdf4 0%, #fff 60%);
}

.pref-chips {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
}

.pref-label {
  font-size: 12px;
  color: #999;
  margin-right: 4px;
}

.ai-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px;
}

.ai-item {
  position: relative;
  transition: transform 0.2s;
}

.ai-item:hover {
  transform: translateY(-2px);
}

.ai-item.top {
  border-color: #18a058;
  background: linear-gradient(135deg, #f0fdf4 0%, #fff 100%);
}

.ai-rank {
  position: absolute;
  top: 8px;
  right: 8px;
  background: #18a058;
  color: #fff;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
}

.ai-image {
  height: 100px;
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 6px;
}

.ai-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.ai-image.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  font-size: 32px;
}

.ai-name {
  margin: 4px 0 8px 0;
  font-size: 14px;
  cursor: pointer;
  color: #333;
}

.ai-name:hover {
  color: #18a058;
}

.ai-reasons {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 8px;
}

.recommend-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.recommend-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.dish-card {
  transition: transform 0.2s;
}

.dish-card:hover {
  transform: translateY(-2px);
}

.dish-image {
  height: 120px;
  overflow: hidden;
  border-radius: 8px;
  margin-bottom: 8px;
}

.dish-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.dish-image.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  font-size: 36px;
}

.dish-info h3 {
  margin-bottom: 8px;
  font-size: 14px;
}

.card-actions {
  margin-top: 8px;
}
</style>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NCard, NButton, NSpace, NTag, NEmpty, NRadioGroup, NRadioButton } from 'naive-ui'
import { useRecommendStore } from '@/stores'
import type { Dish } from '@/types'
import RecordMealModal from '@/components/RecordMealModal.vue'

const recommendStore = useRecommendStore()

const mealType = ref('lunch')
const mood = ref('happy')
const recommendDishes = ref<Dish[]>([])

const showRecordModal = ref(false)
const recordDish = ref<Dish | null>(null)

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
</script>

<template>
  <div class="page-container">
    <h1 class="page-title">智能推荐</h1>

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
.recommend-grid {
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

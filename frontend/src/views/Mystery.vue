<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { NCard, NButton, NSpace, NTag, NEmpty, NSpin } from 'naive-ui'
import { useRecommendStore } from '@/stores'
import RecordMealModal from '@/components/RecordMealModal.vue'
import type { Dish } from '@/types'

const recommendStore = useRecommendStore()
const router = useRouter()

const cards = ref<Array<{ dish: Dish | null; flipped: boolean; chosen: boolean }>>([
  { dish: null, flipped: false, chosen: false },
  { dish: null, flipped: false, chosen: false },
  { dish: null, flipped: false, chosen: false }
])
const loading = ref(false)
const started = ref(false)
const showRecordModal = ref(false)
const recordDish = ref<Dish | null>(null)

async function initCards() {
  loading.value = true
  try {
    if (recommendStore.dailyDishes.length === 0) {
      await recommendStore.fetchDailyRecommend()
    }
    const list = recommendStore.dailyDishes
    if (list.length === 0) {
      cards.value = []
      return
    }
    // 随机选 3 道不重复的菜
    const shuffled = [...list].sort(() => Math.random() - 0.5)
    const picks = shuffled.slice(0, Math.min(3, list.length))
    cards.value = picks.map(dish => ({ dish, flipped: false, chosen: false }))
  } finally {
    loading.value = false
  }
}

onMounted(initCards)

async function start() {
  started.value = true
  await initCards()
}

function pickCard(idx: number) {
  if (started.value && cards.value.some(c => c.flipped)) return
  cards.value[idx].flipped = true
  cards.value[idx].chosen = true
  // 给其它牌也翻开（揭晓模式）
  setTimeout(() => {
    cards.value.forEach((c, i) => {
      if (i !== idx) c.flipped = true
    })
  }, 800)
}

function viewDetail(dish: Dish | null) {
  if (dish) router.push({ name: 'dish-detail', params: { id: dish.id } })
}

function openRecord(dish: Dish) {
  recordDish.value = dish
  showRecordModal.value = true
}

function reset() {
  started.value = false
  cards.value = cards.value.map(c => ({ ...c, flipped: false, chosen: false }))
  initCards()
}
</script>

<template>
  <div class="page-container">
    <h1 class="page-title">盲盒惊喜 🎁</h1>

    <NCard>
      <div v-if="loading" class="loading-wrap">
        <NSpin />
      </div>

      <div v-else-if="cards.length === 0" class="empty-wrap">
        <NEmpty description="菜品库里还没有菜，先去添加吧">
          <template #extra>
            <NButton type="primary" @click="router.push({ name: 'dishes' })">前往添加</NButton>
          </template>
        </NEmpty>
      </div>

      <template v-else>
        <div class="hint">
          <p>三张卡牌背面向下，点击其中一张揭晓今日惊喜菜品 👀</p>
        </div>

        <div class="cards">
          <div
            v-for="(card, idx) in cards"
            :key="idx"
            class="card"
            :class="{ flipped: card.flipped, chosen: card.chosen }"
            @click="pickCard(idx)"
          >
            <div class="card-inner">
              <div class="card-face card-back">
                <div class="card-pattern">?</div>
              </div>
              <div class="card-face card-front">
                <div v-if="card.dish" class="dish-info">
                  <div class="dish-emoji">🍽️</div>
                  <h3>{{ card.dish.name }}</h3>
                  <NSpace>
                    <NTag v-if="card.dish.category" size="small">{{ card.dish.category }}</NTag>
                    <NTag v-if="card.dish.taste" size="small" type="info">{{ card.dish.taste }}</NTag>
                  </NSpace>
                </div>
              </div>
            </div>
          </div>
        </div>

        <NSpace v-if="cards.some(c => c.flipped)" justify="center" style="margin-top: 32px">
          <NButton @click="reset">🔄 再来一次</NButton>
          <NButton
            v-if="cards.find(c => c.chosen)?.dish"
            type="primary"
            @click="openRecord(cards.find(c => c.chosen)!.dish!)"
          >
            就吃这个！记录一餐
          </NButton>
          <NButton
            v-if="cards.find(c => c.chosen)?.dish"
            @click="viewDetail(cards.find(c => c.chosen)?.dish || null)"
          >
            查看详情
          </NButton>
        </NSpace>

        <NSpace v-else justify="center" style="margin-top: 32px">
          <NButton type="primary" size="large" @click="start">开始抽卡</NButton>
        </NSpace>
      </template>
    </NCard>

    <RecordMealModal v-model:show="showRecordModal" :dish="recordDish" />
  </div>
</template>

<style scoped>
.loading-wrap, .empty-wrap {
  display: flex;
  justify-content: center;
  padding: 40px 0;
}

.hint {
  text-align: center;
  color: #666;
  margin-bottom: 24px;
  font-size: 14px;
}

.cards {
  display: flex;
  gap: 24px;
  justify-content: center;
  flex-wrap: wrap;
  perspective: 1000px;
}

.card {
  width: 180px;
  height: 240px;
  cursor: pointer;
  perspective: 1000px;
}

.card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  transition: transform 0.8s cubic-bezier(0.4, 0.2, 0.2, 1);
  transform-style: preserve-3d;
}

.card.flipped .card-inner {
  transform: rotateY(180deg);
}

.card-face {
  position: absolute;
  inset: 0;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  backface-visibility: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.3s;
}

.card:hover .card-face {
  box-shadow: 0 8px 24px rgba(24, 160, 88, 0.2);
}

.card-back {
  background: linear-gradient(135deg, #18a058, #0e7c45);
  color: #fff;
}

.card-pattern {
  font-size: 72px;
  font-weight: 800;
  text-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.card-front {
  background: linear-gradient(135deg, #fff7ed, #fef3c7);
  transform: rotateY(180deg);
  flex-direction: column;
  padding: 16px;
  border: 2px solid #fbbf24;
}

.card.chosen .card-front {
  background: linear-gradient(135deg, #d1fae5, #fef3c7);
  border-color: #18a058;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: rotateY(180deg) scale(1); }
  50% { transform: rotateY(180deg) scale(1.03); }
}

.dish-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  text-align: center;
}

.dish-emoji {
  font-size: 48px;
  margin-bottom: 4px;
}

.dish-info h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

@media (max-width: 640px) {
  .card {
    width: 140px;
    height: 190px;
  }
  .card-pattern {
    font-size: 56px;
  }
  .dish-emoji {
    font-size: 36px;
  }
  .dish-info h3 {
    font-size: 14px;
  }
}
</style>
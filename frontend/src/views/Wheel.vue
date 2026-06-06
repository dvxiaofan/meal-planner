<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NCard, NButton, NSpace, NEmpty, NResult } from 'naive-ui'
import { useRecommendStore } from '@/stores'
import type { Dish } from '@/types'

const recommendStore = useRecommendStore()

const spinning = ref(false)
const selectedDish = ref<Dish | null>(null)
const wheelRotation = ref(0)

onMounted(async () => {
  await recommendStore.fetchDailyRecommend()
})

async function spinWheel() {
  if (spinning.value) return
  
  spinning.value = true
  selectedDish.value = null
  
  // 随机旋转角度
  const spins = 3 + Math.random() * 3 // 3-6圈
  wheelRotation.value += spins * 360
  
  // 模拟旋转延迟
  setTimeout(async () => {
    try {
      const dish = await recommendStore.fetchRandomDish()
      selectedDish.value = dish
    } catch (error) {
      console.error('获取随机菜品失败:', error)
    } finally {
      spinning.value = false
    }
  }, 2000)
}
</script>

<template>
  <div class="page-container">
    <h1 class="page-title">美食转盘</h1>
    
    <NCard>
      <div class="wheel-container">
        <!-- 转盘 -->
        <div class="wheel" :style="{ transform: `rotate(${wheelRotation}deg)` }">
          <div
            v-for="(dish, index) in recommendStore.dailyDishes"
            :key="dish.id"
            class="wheel-item"
            :style="{ transform: `rotate(${index * (360 / recommendStore.dailyDishes.length)}deg)` }"
          >
            {{ dish.name }}
          </div>
        </div>
        
        <!-- 指针 -->
        <div class="pointer">▼</div>
      </div>
      
      <NSpace justify="center" style="margin-top: 24px">
        <NButton type="primary" size="large" @click="spinWheel" :loading="spinning">
          {{ spinning ? '旋转中...' : '开始转盘' }}
        </NButton>
      </NSpace>
      
      <!-- 结果 -->
      <div v-if="selectedDish" class="result">
        <NResult status="success" :title="`今天吃：${selectedDish.name}`">
          <template #footer>
            <NSpace>
              <NTag v-if="selectedDish.category">{{ selectedDish.category }}</NTag>
              <NTag v-if="selectedDish.taste" type="info">{{ selectedDish.taste }}</NTag>
            </NSpace>
          </template>
        </NResult>
      </div>
    </NCard>
  </div>
</template>

<style scoped>
.wheel-container {
  position: relative;
  width: 300px;
  height: 300px;
  margin: 0 auto;
}

.wheel {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 8px solid #18a058;
  position: relative;
  transition: transform 3s cubic-bezier(0.17, 0.67, 0.12, 0.99);
}

.wheel-item {
  position: absolute;
  width: 50%;
  height: 2px;
  top: 50%;
  left: 50%;
  transform-origin: 0 0;
  display: flex;
  align-items: center;
  padding-left: 20px;
  font-size: 12px;
  font-weight: 500;
}

.pointer {
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 32px;
  color: #18a058;
}

.result {
  margin-top: 24px;
  text-align: center;
}
</style>

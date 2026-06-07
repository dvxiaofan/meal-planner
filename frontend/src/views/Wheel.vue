<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { NCard, NButton, NSpace, NEmpty, NResult, NTag } from 'naive-ui'
import { useRecommendStore } from '@/stores'
import { useRouter } from 'vue-router'
import type { Dish } from '@/types'

const recommendStore = useRecommendStore()
const router = useRouter()

const spinning = ref(false)
const selectedDish = ref<Dish | null>(null)
const wheelRotation = ref(0)

const dishes = computed(() => recommendStore.dailyDishes)

onMounted(async () => {
  if (dishes.value.length === 0) {
    await recommendStore.fetchDailyRecommend()
  }
})

function spinWheel() {
  if (spinning.value || dishes.value.length === 0) return

  spinning.value = true
  selectedDish.value = null

  const list = dishes.value
  const N = list.length
  const segAngle = 360 / N
  // 目标索引（在动画开始时本地随机选，最终落点和结果一致）
  const targetIndex = Math.floor(Math.random() * N)
  // 抖动：±0.3 段宽，结果看起来自然
  const jitter = (Math.random() - 0.5) * segAngle * 0.6
  // 指针在 270°（正上），第 i 个 item 的中心线在 wheel-local 角度 = i * segAngle
  // 旋转 R 后屏幕角度 = R + i * segAngle；令其 = 270°
  const targetAngle = 270 - targetIndex * segAngle + jitter
  // 当前角度归一化到 [0, 360)
  const currentMod = ((wheelRotation.value % 360) + 360) % 360
  // 模增量：从 currentMod 走到 targetAngle 需要 +modDelta 度
  const modDelta = (targetAngle - currentMod + 360) % 360
  // 至少 5 圈 + 0~2 圈随机
  const fullSpins = 5 + Math.floor(Math.random() * 3)
  wheelRotation.value += fullSpins * 360 + modDelta

  // 略大于 CSS transition 3s
  setTimeout(() => {
    selectedDish.value = list[targetIndex]
    spinning.value = false
  }, 3200)
}

function viewDetail() {
  if (selectedDish.value) {
    router.push({ name: 'dish-detail', params: { id: selectedDish.value.id } })
  }
}
</script>

<template>
  <div class="page-container">
    <h1 class="page-title">美食转盘</h1>

    <NCard>
      <div v-if="dishes.length === 0" class="empty-wrap">
        <NEmpty description="暂无可转的菜品，请先添加菜品" />
      </div>
      <template v-else>
        <div class="wheel-container">
          <!-- 转盘 -->
          <div class="wheel" :style="{ transform: `rotate(${wheelRotation}deg)` }">
            <div
              v-for="(dish, index) in dishes"
              :key="dish.id"
              class="wheel-item"
              :style="{ transform: `rotate(${index * (360 / dishes.length)}deg)` }"
            >
              <span class="item-name">{{ dish.name }}</span>
            </div>
          </div>
          <!-- 中心圆点 -->
          <div class="wheel-center"></div>
          <!-- 指针 -->
          <div class="pointer">▼</div>
        </div>

        <NSpace justify="center" style="margin-top: 24px">
          <NButton type="primary" size="large" @click="spinWheel" :loading="spinning" :disabled="spinning">
            {{ spinning ? '旋转中...' : '开始转盘' }}
          </NButton>
        </NSpace>
      </template>

      <!-- 结果 -->
      <div v-if="selectedDish" class="result">
        <NResult status="success" :title="`今天吃：${selectedDish.name}`">
          <template #footer>
            <NSpace>
              <NTag v-if="selectedDish.category">{{ selectedDish.category }}</NTag>
              <NTag v-if="selectedDish.taste" type="info">{{ selectedDish.taste }}</NTag>
              <NButton size="small" @click="viewDetail">查看详情</NButton>
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
  width: 360px;
  height: 360px;
  margin: 24px auto;
}

.wheel {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 6px solid #18a058;
  background: conic-gradient(
    from 0deg,
    #fef3c7 0deg 30deg,
    #d1fae5 30deg 60deg,
    #fce7f3 60deg 90deg,
    #ddd6fe 90deg 120deg,
    #ffe4e6 120deg 150deg,
    #e0f2fe 150deg 180deg,
    #d1fae5 180deg 210deg,
    #fef3c7 210deg 240deg,
    #fce7f3 240deg 270deg,
    #ddd6fe 270deg 300deg,
    #ffe4e6 300deg 330deg,
    #e0f2fe 330deg 360deg
  );
  position: relative;
  transition: transform 3s cubic-bezier(0.17, 0.67, 0.12, 0.99);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.wheel-item {
  position: absolute;
  width: 50%;
  height: 30px;
  top: 50%;
  left: 50%;
  transform-origin: 0 0;
  display: flex;
  align-items: center;
  padding-left: 28px;
  margin-top: -15px;
}

.item-name {
  font-size: 13px;
  font-weight: 500;
  color: #333;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
  max-width: 140px;
}

.wheel-center {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #18a058;
  transform: translate(-50%, -50%);
  z-index: 2;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.pointer {
  position: absolute;
  top: -18px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 32px;
  color: #f59e0b;
  z-index: 3;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.empty-wrap {
  padding: 40px 0;
}

.result {
  margin-top: 24px;
  text-align: center;
}

@media (max-width: 480px) {
  .wheel-container {
    width: 280px;
    height: 280px;
  }
  .item-name {
    max-width: 100px;
    font-size: 12px;
  }
}
</style>

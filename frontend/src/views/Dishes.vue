<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  NCard, NButton, NSpace, NInput, NSelect, NTag, NEmpty,
  NSwitch, NPopconfirm, useMessage
} from 'naive-ui'
import { useDishStore } from '@/stores'
import DishFormModal from '@/components/DishFormModal.vue'
import ImageUploader from '@/components/ImageUploader.vue'
import type { DishCreate } from '@/types'

const router = useRouter()
const dishStore = useDishStore()
const message = useMessage()

const search = ref('')
const categoryFilter = ref<string | null>(null)
const tasteFilter = ref<string | null>(null)
const favoriteOnly = ref(false)
const includeDisabled = ref(false)
const showCreateModal = ref(false)

const categoryOptions = [
  { label: '荤菜', value: '荤菜' },
  { label: '素菜', value: '素菜' },
  { label: '汤羹', value: '汤羹' },
  { label: '主食', value: '主食' },
  { label: '凉菜', value: '凉菜' },
  { label: '小吃', value: '小吃' }
]

const tasteOptions = [
  { label: '清淡', value: '清淡' },
  { label: '微辣', value: '微辣' },
  { label: '中辣', value: '中辣' },
  { label: '重辣', value: '重辣' },
  { label: '酸甜', value: '酸甜' },
  { label: '咸鲜', value: '咸鲜' },
  { label: '麻辣', value: '麻辣' },
  { label: '酸辣', value: '酸辣' },
  { label: '五香', value: '五香' },
  { label: '蒜香', value: '蒜香' }
]

const filteredDishes = computed(() => {
  let result = dishStore.dishes

  if (search.value) {
    result = result.filter(dish =>
      dish.name.toLowerCase().includes(search.value.toLowerCase())
    )
  }

  if (categoryFilter.value) {
    result = result.filter(dish => dish.category === categoryFilter.value)
  }

  if (tasteFilter.value) {
    result = result.filter(dish => dish.taste === tasteFilter.value)
  }

  if (favoriteOnly.value) {
    result = result.filter(dish => dish.is_favorite)
  }

  if (!includeDisabled.value) {
    result = result.filter(dish => dish.is_enabled)
  }

  return result
})

onMounted(async () => {
  await dishStore.fetchDishes()
})

async function handleCreate(data: DishCreate) {
  try {
    await dishStore.createDish(data)
    message.success('菜品创建成功')
    showCreateModal.value = false
  } catch {
    message.error('创建失败，请重试')
  }
}

function goToDetail(id: number) {
  router.push({ name: 'dish-detail', params: { id } })
}

async function toggleFavorite(id: number, event: Event) {
  event.stopPropagation()
  try {
    await dishStore.toggleFavorite(id)
  } catch {
    message.error('操作失败')
  }
}

async function toggleEnabled(id: number, event: Event) {
  event.stopPropagation()
  try {
    await dishStore.toggleEnabled(id)
  } catch {
    message.error('操作失败')
  }
}

async function deleteDish(id: number, event: Event) {
  event.stopPropagation()
  try {
    await dishStore.deleteDish(id)
    message.success('已删除')
  } catch {
    message.error('删除失败')
  }
}
</script>

<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">菜品管理</h1>
      <NButton type="primary" @click="showCreateModal = true">
        新增菜品
      </NButton>
    </div>
    
    <!-- 筛选栏 -->
    <NCard style="margin-bottom: 16px">
      <NSpace align="center" :wrap="true">
        <NInput
          v-model:value="search"
          placeholder="搜索菜品名称"
          clearable
          style="width: 200px"
        />
        <NSelect
          v-model:value="categoryFilter"
          :options="categoryOptions"
          placeholder="分类筛选"
          clearable
          style="width: 120px"
        />
        <NSelect
          v-model:value="tasteFilter"
          :options="tasteOptions"
          placeholder="口味筛选"
          clearable
          style="width: 120px"
        />
        <NSpace align="center" :wrap="false">
          <span>只看收藏</span>
          <NSwitch v-model:value="favoriteOnly" />
        </NSpace>
        <NSpace align="center" :wrap="false">
          <span>含已禁用</span>
          <NSwitch v-model:value="includeDisabled" />
        </NSpace>
      </NSpace>
    </NCard>

    <!-- 菜品列表 -->
    <div v-if="filteredDishes.length > 0" class="dish-grid">
      <NCard
        v-for="dish in filteredDishes"
        :key="dish.id"
        class="dish-card"
        :class="{ 'is-disabled': !dish.is_enabled }"
        @click="goToDetail(dish.id)"
      >
        <div class="dish-image">
          <ImageUploader
            :dish-id="dish.id"
            :image-url="dish.image_url"
            size="small"
          />
        </div>
        <div class="dish-info">
          <h3>
            {{ dish.name }}
            <NTag v-if="!dish.is_enabled" size="tiny" type="warning">已禁用</NTag>
          </h3>
          <NSpace>
            <NTag v-if="dish.category" size="small">{{ dish.category }}</NTag>
            <NTag v-if="dish.taste" size="small" type="info">{{ dish.taste }}</NTag>
          </NSpace>
          <div class="dish-meta">
            <span v-if="dish.cook_time">⏱️ {{ dish.cook_time }}分钟</span>
            <span>⭐ {{ dish.difficulty }}</span>
          </div>
          <div class="card-actions" @click.stop>
            <NButton
              size="tiny"
              :type="dish.is_favorite ? 'error' : 'default'"
              @click="toggleFavorite(dish.id, $event)"
            >
              {{ dish.is_favorite ? '★ 已收藏' : '☆ 收藏' }}
            </NButton>
            <NButton
              size="tiny"
              :type="dish.is_enabled ? 'default' : 'warning'"
              @click="toggleEnabled(dish.id, $event)"
            >
              {{ dish.is_enabled ? '已启用' : '已禁用' }}
            </NButton>
            <NPopconfirm @positive-click="deleteDish(dish.id, $event)">
              <template #trigger>
                <NButton size="tiny" type="error" @click.stop>删除</NButton>
              </template>
              确定删除「{{ dish.name }}」？
            </NPopconfirm>
          </div>
        </div>
      </NCard>
    </div>

    <NEmpty v-else description="暂无菜品，点击右上角新增" />

    <!-- 新增弹窗 -->
    <DishFormModal
      v-model:show="showCreateModal"
      @submit="handleCreate"
    />
  </div>
</template>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.dish-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
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
  height: 160px;
  overflow: hidden;
  border-radius: 8px;
  margin-bottom: 12px;
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
  font-size: 48px;
}

.dish-info h3 {
  margin-bottom: 8px;
  font-size: 16px;
}

.dish-meta {
  margin-top: 8px;
  font-size: 12px;
  color: #999;
}

.dish-meta span {
  margin-right: 12px;
}

.is-disabled {
  opacity: 0.6;
}

.card-actions {
  margin-top: 12px;
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}
</style>

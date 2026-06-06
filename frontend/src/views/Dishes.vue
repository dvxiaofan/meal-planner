<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  NCard, NButton, NSpace, NInput, NSelect, NTag, NEmpty,
  NModal, NForm, NFormItem, NInputNumber, NSwitch, NMessageProvider
} from 'naive-ui'
import { useDishStore } from '@/stores'
import type { DishCreate } from '@/types'

const router = useRouter()
const dishStore = useDishStore()

const search = ref('')
const categoryFilter = ref<string | null>(null)
const tasteFilter = ref<string | null>(null)
const showCreateModal = ref(false)
const createForm = ref<DishCreate>({
  name: '',
  category: '',
  taste: '',
  difficulty: 1,
  cook_time: undefined,
  description: ''
})

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
  
  return result
})

onMounted(async () => {
  await dishStore.fetchDishes()
})

async function handleCreate() {
  try {
    await dishStore.createDish(createForm.value)
    showCreateModal.value = false
    resetForm()
  } catch (error) {
    console.error('创建失败:', error)
  }
}

function resetForm() {
  createForm.value = {
    name: '',
    category: '',
    taste: '',
    difficulty: 1,
    cook_time: undefined,
    description: ''
  }
}

function goToDetail(id: number) {
  router.push({ name: 'dish-detail', params: { id } })
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
      <NSpace>
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
      </NSpace>
    </NCard>
    
    <!-- 菜品列表 -->
    <div v-if="filteredDishes.length > 0" class="dish-grid">
      <NCard
        v-for="dish in filteredDishes"
        :key="dish.id"
        class="dish-card"
        @click="goToDetail(dish.id)"
      >
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
          <div class="dish-meta">
            <span v-if="dish.cook_time">⏱️ {{ dish.cook_time }}分钟</span>
            <span>⭐ {{ dish.difficulty }}</span>
          </div>
        </div>
      </NCard>
    </div>
    
    <NEmpty v-else description="暂无菜品，点击右上角新增" />
    
    <!-- 新增弹窗 -->
    <NModal v-model:show="showCreateModal" title="新增菜品" preset="dialog" style="width: 600px">
      <NForm :model="createForm" label-placement="left" label-width="80">
        <NFormItem label="菜品名称" required>
          <NInput v-model:value="createForm.name" placeholder="请输入菜品名称" />
        </NFormItem>
        <NFormItem label="分类" required>
          <NSelect v-model:value="createForm.category" :options="categoryOptions" placeholder="请选择分类" />
        </NFormItem>
        <NFormItem label="口味">
          <NSelect v-model:value="createForm.taste" :options="tasteOptions" placeholder="请选择口味" />
        </NFormItem>
        <NFormItem label="难度">
          <NInputNumber v-model:value="createForm.difficulty" :min="1" :max="5" />
        </NFormItem>
        <NFormItem label="烹饪时间">
          <NInputNumber v-model:value="createForm.cook_time" :min="0" placeholder="分钟" />
        </NFormItem>
        <NFormItem label="简介">
          <NInput v-model:value="createForm.description" type="textarea" placeholder="请输入简介" />
        </NFormItem>
      </NForm>
      <template #action>
        <NSpace>
          <NButton @click="showCreateModal = false">取消</NButton>
          <NButton type="primary" @click="handleCreate">确定</NButton>
        </NSpace>
      </template>
    </NModal>
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
</style>

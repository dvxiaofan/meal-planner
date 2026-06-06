<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NCard, NButton, NSpace, NTag, NEmpty, NDescriptions, NDescriptionsItem,
  NRate, NDivider, NList, NListItem, NThing
} from 'naive-ui'
import { useDishStore } from '@/stores'

const route = useRoute()
const router = useRouter()
const dishStore = useDishStore()

const dishId = Number(route.params.id)

onMounted(async () => {
  if (dishId) {
    await dishStore.fetchDish(dishId)
  }
})

function goBack() {
  router.back()
}

function goToEdit() {
  // TODO: 实现编辑功能
}
</script>

<template>
  <div class="page-container">
    <NButton @click="goBack" style="margin-bottom: 16px">返回</NButton>
    
    <div v-if="dishStore.currentDish" class="dish-detail">
      <NCard>
        <div class="dish-header">
          <div class="dish-image" v-if="dishStore.currentDish.image_url">
            <img :src="dishStore.currentDish.image_url" :alt="dishStore.currentDish.name" />
          </div>
          <div class="dish-image placeholder" v-else>
            🍽️
          </div>
          <div class="dish-basic">
            <h1>{{ dishStore.currentDish.name }}</h1>
            <NSpace>
              <NTag v-if="dishStore.currentDish.category">{{ dishStore.currentDish.category }}</NTag>
              <NTag v-if="dishStore.currentDish.taste" type="info">{{ dishStore.currentDish.taste }}</NTag>
            </NSpace>
            <p v-if="dishStore.currentDish.description" class="description">
              {{ dishStore.currentDish.description }}
            </p>
            <NSpace>
              <NButton type="primary" @click="goToEdit">编辑</NButton>
            </NSpace>
          </div>
        </div>
      </NCard>
      
      <!-- 详细信息 -->
      <NCard title="详细信息" style="margin-top: 16px">
        <NDescriptions bordered>
          <NDescriptionsItem label="分类">
            {{ dishStore.currentDish.category }}
          </NDescriptionsItem>
          <NDescriptionsItem label="口味">
            {{ dishStore.currentDish.taste || '-' }}
          </NDescriptionsItem>
          <NDescriptionsItem label="难度">
            <NRate :value="dishStore.currentDish.difficulty" readonly />
          </NDescriptionsItem>
          <NDescriptionsItem label="烹饪时间">
            {{ dishStore.currentDish.cook_time ? `${dishStore.currentDish.cook_time}分钟` : '-' }}
          </NDescriptionsItem>
          <NDescriptionsItem label="状态">
            <NTag :type="dishStore.currentDish.is_enabled ? 'success' : 'warning'">
              {{ dishStore.currentDish.is_enabled ? '已启用' : '已禁用' }}
            </NTag>
          </NDescriptionsItem>
          <NDescriptionsItem label="收藏">
            <NTag :type="dishStore.currentDish.is_favorite ? 'error' : 'default'">
              {{ dishStore.currentDish.is_favorite ? '已收藏' : '未收藏' }}
            </NTag>
          </NDescriptionsItem>
        </NDescriptions>
      </NCard>
      
      <!-- 食材列表 -->
      <NCard title="食材" style="margin-top: 16px" v-if="dishStore.currentDish.ingredients?.length">
        <NList>
          <NListItem v-for="ingredient in dishStore.currentDish.ingredients" :key="ingredient.id">
            <NThing>
              <template #header>
                {{ ingredient.name }}
              </template>
              <template #description>
                {{ ingredient.amount || '-' }} {{ ingredient.type ? `(${ingredient.type})` : '' }}
              </template>
            </NThing>
          </NListItem>
        </NList>
      </NCard>
      
      <!-- 烹饪步骤 -->
      <NCard title="烹饪步骤" style="margin-top: 16px" v-if="dishStore.currentDish.steps?.length">
        <NList>
          <NListItem v-for="step in dishStore.currentDish.steps" :key="step.id">
            <NThing>
              <template #header>
                步骤 {{ step.step_number }}
              </template>
              <template #description>
                {{ step.description }}
                <span v-if="step.duration"> ({{ step.duration }}秒)</span>
              </template>
            </NThing>
          </NListItem>
        </NList>
      </NCard>
    </div>
    
    <NEmpty v-else description="菜品不存在" />
  </div>
</template>

<style scoped>
.dish-header {
  display: flex;
  gap: 24px;
}

.dish-image {
  width: 300px;
  height: 200px;
  border-radius: 12px;
  overflow: hidden;
  flex-shrink: 0;
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
  font-size: 64px;
}

.dish-basic {
  flex: 1;
}

.dish-basic h1 {
  margin-bottom: 12px;
  font-size: 24px;
}

.description {
  margin-top: 12px;
  color: #666;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .dish-header {
    flex-direction: column;
  }
  
  .dish-image {
    width: 100%;
    height: 200px;
  }
}
</style>

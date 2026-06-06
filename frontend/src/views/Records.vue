<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NCard, NEmpty, NList, NListItem, NThing, NTag, NRate } from 'naive-ui'
import { useRecordStore } from '@/stores'

const recordStore = useRecordStore()

onMounted(async () => {
  await recordStore.fetchRecords()
})

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}
</script>

<template>
  <div class="page-container">
    <h1 class="page-title">用餐记录</h1>
    
    <NCard>
      <NList v-if="recordStore.records.length > 0">
        <NListItem v-for="record in recordStore.records" :key="record.id">
          <NThing>
            <template #header>
              {{ record.dish?.name || '未知菜品' }}
            </template>
            <template #description>
              <NSpace>
                <NTag size="small">{{ record.meal_type }}</NTag>
                <NTag size="small" type="info">{{ formatDate(record.record_date) }}</NTag>
                <NRate v-if="record.rating" :value="record.rating" readonly size="small" />
              </NSpace>
              <p v-if="record.note" style="margin-top: 8px; color: #666">
                {{ record.note }}
              </p>
            </template>
          </NThing>
        </NListItem>
      </NList>
      <NEmpty v-else description="暂无用餐记录" />
    </NCard>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { NCard, NEmpty, NList, NListItem, NThing, NTag, NRate, NTabs, NTabPane, NSpin, NButton, NImage, NIcon, NUpload, useMessage } from 'naive-ui'
import { CameraOutline } from '@vicons/ionicons5'
import { recordApi, dishApi } from '@/api'
import { useRecordStore } from '@/stores'
import type { MealRecord } from '@/types'

const recordStore = useRecordStore()
const router = useRouter()
const message = useMessage()
const activeTab = ref('list')
const loading = ref(false)
const uploadingFor = ref<number | null>(null)

const photos = computed<MealRecord[]>(() =>
  recordStore.records.filter(r => r.photo_url)
)

onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([
      recordStore.fetchRecords(),
      recordStore.fetchTimeline(100)
    ])
  } finally {
    loading.value = false
  }
})

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

function goToDish(dishId?: number) {
  if (dishId) router.push({ name: 'dish-detail', params: { id: dishId } })
}

async function onPhotoSelect(recordId: number, options: { fileList: Array<{ file: File }> }) {
  const file = options.fileList[0]?.file
  if (!file) return
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
    message.error('仅支持 JPG / PNG / WebP')
    return false
  }
  if (file.size > 5 * 1024 * 1024) {
    message.error('图片不能超过 5MB')
    return false
  }
  uploadingFor.value = recordId
  try {
    const form = new FormData()
    form.append('file', file)
    const { photo_url } = await recordApi.uploadPhoto(recordId, form)
    // 更新本地状态
    const r = recordStore.records.find(x => x.id === recordId)
    if (r) r.photo_url = photo_url
    const tr = recordStore.timeline.find(x => x.id === recordId)
    if (tr) tr.photo_url = photo_url
    message.success('照片已上传')
  } catch {
    // 拦截器处理
  } finally {
    uploadingFor.value = null
  }
  return false  // 阻止 NUpload 默认上传
}

// 合并：时间线按日期降序
const recordsByDate = computed(() => {
  const groups = new Map<string, MealRecord[]>()
  for (const r of recordStore.records) {
    const d = r.record_date?.slice(0, 10) || '未知'
    if (!groups.has(d)) groups.set(d, [])
    groups.get(d)!.push(r)
  }
  return Array.from(groups.entries()).sort((a, b) => b[0].localeCompare(a[0]))
})
</script>

<template>
  <div class="page-container">
    <h1 class="page-title">用餐记录</h1>

    <NCard>
      <NTabs v-model:value="activeTab" type="line" animated>
        <NTabPane name="list" tab="📋 列表">
          <NSpin :show="loading">
            <NEmpty v-if="recordStore.records.length === 0" description="暂无用餐记录">
              <template #extra>
                <NButton type="primary" @click="router.push({ name: 'home' })">去首页记录</NButton>
              </template>
            </NEmpty>

            <div v-else>
              <div v-for="[date, items] in recordsByDate" :key="date" class="date-group">
                <h4 class="date-title">{{ date }}</h4>
                <NList>
                  <NListItem v-for="record in items" :key="record.id">
                    <NThing>
                      <template #header>
                        <span class="dish-link" @click="goToDish(record.dish_id)">
                          {{ record.dish?.name || '未知菜品' }}
                        </span>
                      </template>
                      <template #description>
                        <NSpace>
                          <NTag size="small" :type="record.meal_type === 'lunch' ? 'success' : 'info'">
                            {{ record.meal_type === 'lunch' ? '午餐' : '晚餐' }}
                          </NTag>
                          <NRate v-if="record.rating" :value="record.rating" readonly size="small" />
                          <NUpload
                            :show-file-list="false"
                            accept="image/jpeg,image/png,image/webp"
                            @change="(o: any) => onPhotoSelect(record.id, o)"
                          >
                            <NButton
                              size="tiny"
                              :loading="uploadingFor === record.id"
                              :type="record.photo_url ? 'success' : 'default'"
                              ghost
                            >
                              <template #icon><NIcon :component="CameraOutline" /></template>
                              {{ record.photo_url ? '换照片' : '传照片' }}
                            </NButton>
                          </NUpload>
                        </NSpace>
                        <p v-if="record.note" class="note">{{ record.note }}</p>
                        <div v-if="record.photo_url" class="photo-thumb">
                          <NImage :src="record.photo_url" :alt="record.dish?.name" object-fit="cover" />
                        </div>
                      </template>
                    </NThing>
                  </NListItem>
                </NList>
              </div>
            </div>
          </NSpin>
        </NTabPane>

        <NTabPane name="photo" tab="📷 照片墙">
          <NSpin :show="loading">
            <NEmpty v-if="photos.length === 0" description="还没有照片记录">
              <template #extra>
                <NButton type="primary" @click="router.push({ name: 'home' })">去添加</NButton>
              </template>
            </NEmpty>

            <div v-else class="masonry">
              <div
                v-for="record in photos"
                :key="record.id"
                class="masonry-item"
                @click="goToDish(record.dish_id)"
              >
                <NImage
                  :src="record.photo_url"
                  :alt="record.dish?.name"
                  object-fit="cover"
                  preview-disabled
                  style="border-radius: 8px 8px 0 0"
                />
                <div class="masonry-meta">
                  <div class="masonry-name">{{ record.dish?.name }}</div>
                  <div class="masonry-date">
                    <NTag size="tiny" :type="record.meal_type === 'lunch' ? 'success' : 'info'">
                      {{ record.meal_type === 'lunch' ? '午' : '晚' }}
                    </NTag>
                    <span>{{ formatDate(record.record_date) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </NSpin>
        </NTabPane>
      </NTabs>
    </NCard>
  </div>
</template>

<style scoped>
.date-group {
  margin-bottom: 24px;
}

.date-title {
  font-size: 14px;
  color: #999;
  margin: 0 0 12px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
}

.dish-link {
  cursor: pointer;
  color: #18a058;
}

.dish-link:hover {
  text-decoration: underline;
}

.note {
  margin-top: 8px;
  color: #666;
  font-size: 13px;
  line-height: 1.5;
}

.photo-thumb {
  margin-top: 8px;
  max-width: 240px;
  border-radius: 6px;
  overflow: hidden;
}

.photo-thumb :deep(img) {
  width: 100%;
  display: block;
}

/* 瀑布流 */
.masonry {
  column-count: 3;
  column-gap: 16px;
}

.masonry-item {
  break-inside: avoid;
  margin-bottom: 16px;
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: transform 0.2s;
  display: inline-block;
  width: 100%;
}

.masonry-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.masonry-meta {
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.masonry-name {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.masonry-date {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #999;
}

@media (max-width: 900px) {
  .masonry {
    column-count: 2;
  }
}

@media (max-width: 540px) {
  .masonry {
    column-count: 1;
  }
}
</style>
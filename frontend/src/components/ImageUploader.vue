<script setup lang="ts">
import { ref } from 'vue'
import { NIcon, NSpin, useMessage } from 'naive-ui'
import { CameraOutline } from '@vicons/ionicons5'
import { useDishStore } from '@/stores'

interface Props {
  dishId: number
  imageUrl?: string | null
  // 圆角尺寸
  size?: 'small' | 'medium' | 'large'
}

const props = withDefaults(defineProps<Props>(), {
  imageUrl: null,
  size: 'medium'
})

const emit = defineEmits<{
  'updated': [imageUrl: string]
}>()

const dishStore = useDishStore()
const message = useMessage()

const fileInputRef = ref<HTMLInputElement | null>(null)
const uploading = ref(false)

const height = props.size === 'small' ? '120px' : props.size === 'large' ? '220px' : '180px'

function openFilePicker() {
  fileInputRef.value?.click()
}

async function handleFileChange(e: Event) {
  const target = e.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  // 简单校验
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
    message.error('仅支持 JPG / PNG / WebP 格式')
    return
  }
  if (file.size > 5 * 1024 * 1024) {
    message.error('图片大小不能超过 5MB')
    return
  }
  uploading.value = true
  try {
    const url = await dishStore.uploadImage(props.dishId, file)
    message.success('图片已更新')
    emit('updated', url)
  } catch {
    message.error('上传失败，请重试')
  } finally {
    uploading.value = false
    // 允许重复选择同一文件
    target.value = ''
  }
}
</script>

<template>
  <div class="uploader" :style="{ height }" @click.stop="openFilePicker">
    <img v-if="imageUrl" :src="imageUrl" :alt="`菜品 ${dishId}`" />
    <div v-else class="placeholder">
      <NIcon :component="CameraOutline" :size="32" />
      <span>点击上传图片</span>
    </div>
    <div v-if="uploading" class="overlay">
      <NSpin size="medium" />
    </div>
    <div v-else class="hint">
      <NIcon :component="CameraOutline" />
      <span>{{ imageUrl ? '换一张' : '上传' }}</span>
    </div>
    <input
      ref="fileInputRef"
      type="file"
      accept="image/jpeg,image/png,image/webp"
      hidden
      @change="handleFileChange"
    />
  </div>
</template>

<style scoped>
.uploader {
  position: relative;
  width: 100%;
  border-radius: 12px;
  overflow: hidden;
  background: #f5f5f5;
  cursor: pointer;
  transition: opacity 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.uploader:hover {
  opacity: 0.92;
}

.uploader img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #999;
  font-size: 13px;
}

.hint {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.55);
  color: #fff;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.uploader:hover .hint {
  opacity: 1;
}

.overlay {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
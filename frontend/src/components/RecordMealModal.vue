<script setup lang="ts">
import { ref, watch, reactive, computed } from 'vue'
import {
  NModal, NForm, NFormItem, NRadioGroup, NRadioButton,
  NRate, NInput, NDatePicker, NSpace, NButton, NTag
} from 'naive-ui'
import { useMessage } from 'naive-ui'
import type { Dish } from '@/types'
import { useRecordStore } from '@/stores'

interface Props {
  show: boolean
  dish: Dish | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:show': [value: boolean]
  'created': []
}>()

const recordStore = useRecordStore()
const message = useMessage()

// 默认时间：现在
function nowTimestamp() {
  return Date.now()
}

const form = reactive({
  meal_type: 'lunch' as 'lunch' | 'dinner',
  rating: 0 as number,
  note: '',
  record_date: nowTimestamp()
})

const submitting = ref(false)

const dishName = computed(() => props.dish?.name ?? '')

watch(
  () => props.show,
  (show) => {
    if (show) {
      // 根据当前时间推断午/晚餐
      const h = new Date().getHours()
      form.meal_type = h < 15 ? 'lunch' : 'dinner'
      form.rating = 0
      form.note = ''
      form.record_date = Date.now()
    }
  }
)

function handleCancel() {
  emit('update:show', false)
}

async function handleConfirm() {
  if (!props.dish) return
  submitting.value = true
  try {
    await recordStore.createRecord({
      dish_id: props.dish.id,
      meal_type: form.meal_type,
      rating: form.rating || undefined,
      note: form.note.trim() || undefined,
      record_date: new Date(form.record_date).toISOString()
    })
    message.success(`已记录：${dishName.value}`)
    emit('created')
    emit('update:show', false)
  } catch (e) {
    message.error('记录失败，请重试')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <NModal
    :show="show"
    preset="card"
    :title="`记录一餐：${dishName}`"
    style="width: 520px; max-width: 95vw"
    :mask-closable="false"
    @update:show="emit('update:show', $event)"
  >
    <NForm label-placement="top">
      <NFormItem label="餐型">
        <NRadioGroup v-model:value="form.meal_type">
          <NRadioButton value="lunch">午餐</NRadioButton>
          <NRadioButton value="dinner">晚餐</NRadioButton>
        </NRadioGroup>
      </NFormItem>

      <NFormItem label="评分">
        <NRate v-model:value="form.rating" :count="5" />
      </NFormItem>

      <NFormItem label="用餐时间">
        <NDatePicker
          v-model:value="form.record_date"
          type="datetime"
          format="yyyy-MM-dd HH:mm"
          style="width: 100%"
        />
      </NFormItem>

      <NFormItem label="备注">
        <NInput
          v-model:value="form.note"
          type="textarea"
          placeholder="说说今天的菜怎么样..."
          :autosize="{ minRows: 2, maxRows: 4 }"
        />
      </NFormItem>

      <div v-if="dish" class="dish-meta">
        <NTag size="small" v-if="dish.category">{{ dish.category }}</NTag>
        <NTag size="small" type="info" v-if="dish.taste">{{ dish.taste }}</NTag>
        <NTag size="small" type="warning" v-if="dish.cook_time">⏱ {{ dish.cook_time }}分钟</NTag>
      </div>
    </NForm>

    <template #footer>
      <NSpace justify="end">
        <NButton @click="handleCancel">取消</NButton>
        <NButton type="primary" :loading="submitting" @click="handleConfirm">
          记录
        </NButton>
      </NSpace>
    </template>
  </NModal>
</template>

<style scoped>
.dish-meta {
  display: flex;
  gap: 8px;
  margin-top: -8px;
}
</style>
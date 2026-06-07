<script setup lang="ts">
import { ref, watch, computed, reactive } from 'vue'
import {
  NModal, NForm, NFormItem, NInput, NSelect, NInputNumber, NButton,
  NSpace, NDivider, NIcon
} from 'naive-ui'
import { AddOutline, TrashOutline } from '@vicons/ionicons5'
import type { Dish, DishCreate, DishUpdate, IngredientCreate, StepCreate } from '@/types'

interface Props {
  show: boolean
  dish?: Dish | null
}

const props = withDefaults(defineProps<Props>(), {
  dish: null
})

const emit = defineEmits<{
  'update:show': [value: boolean]
  submit: [data: DishCreate | DishUpdate]
}>()

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

const ingredientTypeOptions = [
  { label: '主料', value: '主料' },
  { label: '调料', value: '调料' }
]

interface IngredientRow extends IngredientCreate {}
interface StepRow extends StepCreate {}

const form = reactive({
  name: '',
  category: '' as string,
  taste: null as string | null,
  difficulty: 1,
  cook_time: null as number | null,
  description: '' as string,
  ingredients: [] as IngredientRow[],
  steps: [] as StepRow[]
})

const isEdit = computed(() => !!props.dish)

function resetForm() {
  form.name = ''
  form.category = ''
  form.taste = null
  form.difficulty = 1
  form.cook_time = null
  form.description = ''
  form.ingredients = []
  form.steps = []
}

function loadFromDish(dish: Dish) {
  form.name = dish.name
  form.category = dish.category
  form.taste = dish.taste ?? null
  form.difficulty = dish.difficulty
  form.cook_time = dish.cook_time ?? null
  form.description = dish.description ?? ''
  form.ingredients = (dish.ingredients ?? []).map(i => ({
    name: i.name,
    amount: i.amount,
    type: i.type
  }))
  form.steps = (dish.steps ?? []).map(s => ({
    step_number: s.step_number,
    description: s.description,
    duration: s.duration
  }))
}

watch(
  () => [props.show, props.dish],
  ([show, dish]) => {
    if (!show) return
    if (dish) {
      loadFromDish(dish as Dish)
    } else {
      resetForm()
    }
  },
  { immediate: true }
)

function addIngredient() {
  form.ingredients.push({ name: '', amount: '', type: '主料' })
}

function removeIngredient(idx: number) {
  form.ingredients.splice(idx, 1)
}

function addStep() {
  form.steps.push({
    step_number: form.steps.length + 1,
    description: '',
    duration: undefined
  })
}

function removeStep(idx: number) {
  form.steps.splice(idx, 1)
  form.steps.forEach((s, i) => (s.step_number = i + 1))
}

const formRef = ref()
const rules = {
  name: { required: true, message: '请输入菜品名称', trigger: ['blur', 'input'] },
  category: { required: true, message: '请选择分类', trigger: ['blur', 'change'] }
}

function handleCancel() {
  emit('update:show', false)
}

async function handleConfirm() {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }
  // 过滤空行
  const cleanIngredients: IngredientCreate[] = form.ingredients
    .filter(i => i.name?.trim())
    .map(i => ({
      name: i.name.trim(),
      amount: i.amount?.trim() || undefined,
      type: i.type || undefined
    }))
  const cleanSteps: StepCreate[] = form.steps
    .filter(s => s.description?.trim())
    .map((s, i) => ({
      step_number: i + 1,
      description: s.description.trim(),
      duration: s.duration ?? undefined
    }))

  const baseData = {
    name: form.name.trim(),
    category: form.category,
    taste: form.taste || undefined,
    difficulty: form.difficulty,
    cook_time: form.cook_time ?? undefined,
    description: form.description?.trim() || undefined,
    ingredients: cleanIngredients,
    steps: cleanSteps
  }

  emit('submit', baseData)
}
</script>

<template>
  <NModal
    :show="show"
    preset="card"
    :title="isEdit ? '编辑菜品' : '新增菜品'"
    style="width: 720px; max-width: 95vw"
    :mask-closable="false"
    @update:show="emit('update:show', $event)"
  >
    <NForm
      ref="formRef"
      :model="form"
      :rules="rules"
      label-placement="top"
    >
      <div class="form-grid">
        <NFormItem label="菜品名称" path="name">
          <NInput v-model:value="form.name" placeholder="请输入菜品名称" />
        </NFormItem>
        <NFormItem label="分类" path="category">
          <NSelect
            v-model:value="form.category"
            :options="categoryOptions"
            placeholder="请选择分类"
          />
        </NFormItem>
        <NFormItem label="口味">
          <NSelect
            v-model:value="form.taste"
            :options="tasteOptions"
            placeholder="请选择口味"
            clearable
          />
        </NFormItem>
        <NFormItem label="难度">
          <NInputNumber v-model:value="form.difficulty" :min="1" :max="5" style="width: 100%" />
        </NFormItem>
        <NFormItem label="烹饪时间（分钟）">
          <NInputNumber v-model:value="form.cook_time" :min="0" placeholder="分钟" style="width: 100%" />
        </NFormItem>
        <NFormItem label="简介" class="full-row">
          <NInput
            v-model:value="form.description"
            type="textarea"
            placeholder="请输入简介"
            :autosize="{ minRows: 2, maxRows: 4 }"
          />
        </NFormItem>
      </div>

      <NDivider title-placement="left">食材</NDivider>
      <div class="dynamic-list">
        <div
          v-for="(ing, idx) in form.ingredients"
          :key="`ing-${idx}`"
          class="dynamic-row"
        >
          <NInput
            v-model:value="ing.name"
            placeholder="食材名"
            style="width: 140px"
          />
          <NInput
            v-model:value="ing.amount"
            placeholder="用量（如 200g）"
            style="width: 140px"
          />
          <NSelect
            v-model:value="ing.type"
            :options="ingredientTypeOptions"
            placeholder="类型"
            style="width: 100px"
          />
          <NButton text type="error" @click="removeIngredient(idx)">
            <template #icon><NIcon :component="TrashOutline" /></template>
          </NButton>
        </div>
        <NButton dashed block @click="addIngredient">
          <template #icon><NIcon :component="AddOutline" /></template>
          添加食材
        </NButton>
      </div>

      <NDivider title-placement="left">烹饪步骤</NDivider>
      <div class="dynamic-list">
        <div
          v-for="(st, idx) in form.steps"
          :key="`step-${idx}`"
          class="dynamic-row step-row"
        >
          <span class="step-num">{{ idx + 1 }}</span>
          <NInput
            v-model:value="st.description"
            type="textarea"
            placeholder="步骤描述"
            :autosize="{ minRows: 1, maxRows: 3 }"
            style="flex: 1"
          />
          <NInputNumber
            v-model:value="st.duration"
            placeholder="秒"
            :min="0"
            style="width: 120px"
          />
          <NButton text type="error" @click="removeStep(idx)">
            <template #icon><NIcon :component="TrashOutline" /></template>
          </NButton>
        </div>
        <NButton dashed block @click="addStep">
          <template #icon><NIcon :component="AddOutline" /></template>
          添加步骤
        </NButton>
      </div>
    </NForm>

    <template #footer>
      <NSpace justify="end">
        <NButton @click="handleCancel">取消</NButton>
        <NButton type="primary" @click="handleConfirm">
          {{ isEdit ? '保存' : '创建' }}
        </NButton>
      </NSpace>
    </template>
  </NModal>
</template>

<style scoped>
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0 16px;
}

.form-grid :deep(.full-row) {
  grid-column: 1 / -1;
}

.dynamic-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.dynamic-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.step-row {
  align-items: flex-start;
}

.step-num {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #18a058;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
  margin-top: 4px;
}

@media (max-width: 640px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
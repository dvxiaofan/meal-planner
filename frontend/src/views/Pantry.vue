<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  NCard, NButton, NSpace, NInput, NSelect, NTag, NEmpty, NSpin,
  NModal, NForm, NFormItem, NInputNumber, NPopconfirm, NDivider, useMessage, NGrid, NGi
} from 'naive-ui'
import { AddOutline, TrashOutline, CheckmarkCircle, EllipsisHorizontalCircleOutline } from '@vicons/ionicons5'
import { pantryApi } from '@/api'
import type { PantryItem } from '@/types'

const message = useMessage()
const loading = ref(false)
const items = ref<PantryItem[]>([])
const search = ref('')
const categoryFilter = ref<string | null>(null)
const stockFilter = ref<string | null>('in_stock') // 'in_stock' | 'all' | 'out'
const showEditModal = ref(false)
const editing = ref<PantryItem | null>(null)
const isCreate = ref(false)

const form = ref({
  name: '',
  amount: '',
  unit: '',
  category: null as string | null,
  note: '',
  in_stock: true
})

const categoryOptions = [
  { label: '蔬菜', value: '蔬菜' },
  { label: '肉类', value: '肉类' },
  { label: '海鲜', value: '海鲜' },
  { label: '蛋奶', value: '蛋奶' },
  { label: '主食', value: '主食' },
  { label: '调料', value: '调料' },
  { label: '水果', value: '水果' },
  { label: '其它', value: '其它' }
]

const stockOptions = [
  { label: '有库存', value: 'in_stock' },
  { label: '全部', value: 'all' },
  { label: '已用完', value: 'out' }
]

const filtered = computed(() => {
  let r = items.value
  if (search.value) {
    r = r.filter(i => i.name.toLowerCase().includes(search.value.toLowerCase()))
  }
  if (categoryFilter.value) {
    r = r.filter(i => i.category === categoryFilter.value)
  }
  if (stockFilter.value === 'in_stock') {
    r = r.filter(i => i.in_stock)
  } else if (stockFilter.value === 'out') {
    r = r.filter(i => !i.in_stock)
  }
  return r
})

const grouped = computed(() => {
  const map = new Map<string, PantryItem[]>()
  for (const it of filtered.value) {
    const k = it.category || '其它'
    if (!map.has(k)) map.set(k, [])
    map.get(k)!.push(it)
  }
  return Array.from(map.entries()).map(([category, list]) => ({ category, list }))
})

const stats = computed(() => ({
  total: items.value.length,
  inStock: items.value.filter(i => i.in_stock).length,
  outOfStock: items.value.filter(i => !i.in_stock).length
}))

async function fetchAll() {
  loading.value = true
  try {
    items.value = await pantryApi.list()
  } finally {
    loading.value = false
  }
}

function openCreate() {
  isCreate.value = true
  editing.value = null
  form.value = { name: '', amount: '', unit: '', category: null, note: '', in_stock: true }
  showEditModal.value = true
}

function openEdit(item: PantryItem) {
  isCreate.value = false
  editing.value = item
  form.value = {
    name: item.name,
    amount: item.amount || '',
    unit: item.unit || '',
    category: item.category || null,
    note: item.note || '',
    in_stock: item.in_stock
  }
  showEditModal.value = true
}

async function saveItem() {
  if (!form.value.name.trim()) {
    message.warning('请输入食材名称')
    return
  }
  const payload = {
    name: form.value.name.trim(),
    amount: form.value.amount.trim() || undefined,
    unit: form.value.unit.trim() || undefined,
    category: form.value.category || undefined,
    note: form.value.note.trim() || undefined,
    in_stock: form.value.in_stock
  }
  try {
    if (isCreate.value) {
      await pantryApi.create(payload)
      message.success('已加入库存')
    } else if (editing.value) {
      await pantryApi.update(editing.value.id, payload)
      message.success('已更新')
    }
    showEditModal.value = false
    await fetchAll()
  } catch {
    // 拦截器已处理
  }
}

async function toggleStock(item: PantryItem) {
  try {
    const { in_stock } = await pantryApi.toggleInStock(item.id)
    const idx = items.value.findIndex(i => i.id === item.id)
    if (idx >= 0) items.value[idx].in_stock = in_stock
  } catch {
    // 拦截器已处理
  }
}

async function removeItem(item: PantryItem) {
  try {
    await pantryApi.remove(item.id)
    items.value = items.value.filter(i => i.id !== item.id)
    message.success('已删除')
  } catch {
    // 拦截器已处理
  }
}

onMounted(fetchAll)
</script>

<template>
  <div class="page-container">
    <h1 class="page-title">食材库存 🧊</h1>

    <NSpace vertical :size="16">
      <!-- 顶部统计 -->
      <NGrid :cols="3" :x-gap="16">
        <NGi>
          <NCard>
            <div class="stat-label">总条目</div>
            <div class="stat-value">{{ stats.total }}</div>
          </NCard>
        </NGi>
        <NGi>
          <NCard>
            <div class="stat-label">有库存</div>
            <div class="stat-value text-success">{{ stats.inStock }}</div>
          </NCard>
        </NGi>
        <NGi>
          <NCard>
            <div class="stat-label">已用完</div>
            <div class="stat-value text-warn">{{ stats.outOfStock }}</div>
          </NCard>
        </NGi>
      </NGrid>

      <!-- 筛选栏 -->
      <NCard>
        <NSpace :wrap="true" align="center">
          <NInput v-model:value="search" placeholder="搜索食材" clearable style="width: 200px" />
          <NSelect
            v-model:value="categoryFilter"
            :options="categoryOptions"
            placeholder="分类筛选"
            clearable
            style="width: 140px"
          />
          <NSelect
            v-model:value="stockFilter"
            :options="stockOptions"
            placeholder="库存状态"
            style="width: 130px"
          />
          <NButton type="primary" @click="openCreate">
            ➕ 添加库存
          </NButton>
        </NSpace>
      </NCard>

      <NSpin :show="loading">
        <NEmpty v-if="items.length === 0" description="库存空空，先添加一些常备食材吧" />
        <NEmpty v-else-if="filtered.length === 0" description="没有匹配的食材" />

        <div v-for="group in grouped" :key="group.category">
          <h3 class="group-title">
            <NTag :type="group.category === '调料' ? 'warning' : 'success'" size="small">{{ group.category }}</NTag>
            {{ group.category }} · {{ group.list.length }}
          </h3>
          <NGrid :cols="4" :x-gap="12" :y-gap="12" responsive="screen" :item-responsive="true">
            <NGi v-for="item in group.list" :key="item.id" span="4 m:2 l:1">
              <div class="pantry-item" :class="{ 'out-of-stock': !item.in_stock }">
                <div class="item-header">
                  <div class="item-name">{{ item.name }}</div>
                  <NTag v-if="!item.in_stock" type="warning" size="tiny">已用完</NTag>
                </div>
                <div class="item-amount" v-if="item.amount || item.unit">
                  {{ item.amount }}{{ item.unit ? ' ' + item.unit : '' }}
                </div>
                <div v-else class="item-amount text-muted">用量未填</div>
                <div v-if="item.note" class="item-note">{{ item.note }}</div>
                <div class="item-actions" @click.stop>
                  <NButton
                    size="tiny"
                    :type="item.in_stock ? 'success' : 'default'"
                    ghost
                    @click="toggleStock(item)"
                  >
                    {{ item.in_stock ? '✓ 有货' : '○ 已用完' }}
                  </NButton>
                  <NButton size="tiny" @click="openEdit(item)">编辑</NButton>
                  <NPopconfirm @positive-click="removeItem(item)">
                    <template #trigger>
                      <NButton size="tiny" type="error" ghost>删除</NButton>
                    </template>
                    删除「{{ item.name }}」？
                  </NPopconfirm>
                </div>
              </div>
            </NGi>
          </NGrid>
        </div>
      </NSpin>
    </NSpace>

    <!-- 编辑/新增弹窗 -->
    <NModal
      v-model:show="showEditModal"
      preset="card"
      :title="isCreate ? '添加库存' : '编辑库存'"
      style="width: 520px; max-width: 95vw"
    >
      <NForm :model="form" label-placement="top">
        <NFormItem label="食材名称" required>
          <NInput v-model:value="form.name" placeholder="如：番茄" />
        </NFormItem>
        <div style="display: flex; gap: 12px">
          <NFormItem label="用量" style="flex: 1">
            <NInput v-model:value="form.amount" placeholder="如：500" />
          </NFormItem>
          <NFormItem label="单位" style="width: 120px">
            <NInput v-model:value="form.unit" placeholder="g / 个" />
          </NFormItem>
        </div>
        <NFormItem label="分类">
          <NSelect v-model:value="form.category" :options="categoryOptions" placeholder="选择分类" clearable />
        </NFormItem>
        <NFormItem label="备注">
          <NInput v-model:value="form.note" type="textarea" placeholder="选填" :autosize="{ minRows: 1, maxRows: 3 }" />
        </NFormItem>
        <NFormItem label="状态">
          <NSpace>
            <NButton
              size="small"
              :type="form.in_stock ? 'success' : 'default'"
              @click="form.in_stock = true"
            >✓ 有货</NButton>
            <NButton
              size="small"
              :type="!form.in_stock ? 'warning' : 'default'"
              @click="form.in_stock = false"
            >○ 已用完</NButton>
          </NSpace>
        </NFormItem>
      </NForm>
      <template #footer>
        <NSpace justify="end">
          <NButton @click="showEditModal = false">取消</NButton>
          <NButton type="primary" @click="saveItem">保存</NButton>
        </NSpace>
      </template>
    </NModal>
  </div>
</template>

<style scoped>
.stat-label {
  font-size: 13px;
  color: #999;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #333;
}

.text-success { color: #18a058; }
.text-warn { color: #f0a020; }
.text-muted { color: #bbb; }

.group-title {
  font-size: 15px;
  margin: 16px 0 12px 0;
  color: #333;
  display: flex;
  align-items: center;
  gap: 8px;
}

.pantry-item {
  background: #fff;
  border: 1px solid #f0f0f0;
  border-radius: 10px;
  padding: 12px;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 6px;
  transition: all 0.2s;
}

.pantry-item:hover {
  border-color: #18a058;
  box-shadow: 0 2px 12px rgba(24, 160, 88, 0.1);
}

.pantry-item.out-of-stock {
  opacity: 0.65;
  background: #fafafa;
}

.item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.item-name {
  font-size: 15px;
  font-weight: 500;
  color: #333;
  flex: 1;
}

.item-amount {
  font-size: 13px;
  color: #666;
}

.item-note {
  font-size: 12px;
  color: #999;
  font-style: italic;
}

.item-actions {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  margin-top: 4px;
}
</style>
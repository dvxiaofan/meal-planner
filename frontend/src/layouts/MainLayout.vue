<script setup lang="ts">
import { ref, computed, h, onMounted, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  NLayout, NLayoutSider, NLayoutContent, NLayoutHeader,
  NMenu, NIcon, NDrawer, NDrawerContent, NButton, NSpace, NTag
} from 'naive-ui'
import type { MenuOption } from 'naive-ui'
import {
  HomeOutline, RestaurantOutline, StarOutline, TimeOutline,
  CalendarOutline, TrophyOutline, StatsChartOutline, ColorWandOutline,
  GiftOutline, MenuOutline
} from '@vicons/ionicons5'

const router = useRouter()
const route = useRoute()
const collapsed = ref(false)
const showMobileDrawer = ref(false)
const isMobile = ref(false)

function checkMobile() {
  if (typeof window === 'undefined') return
  isMobile.value = window.innerWidth <= 768
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})
onBeforeUnmount(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('resize', checkMobile)
  }
})

const menuOptions: MenuOption[] = [
  { label: '首页', key: 'home', icon: () => h(NIcon, null, { default: () => h(HomeOutline) }) },
  { label: '菜品管理', key: 'dishes', icon: () => h(NIcon, null, { default: () => h(RestaurantOutline) }) },
  { label: '智能推荐', key: 'recommend', icon: () => h(NIcon, null, { default: () => h(ColorWandOutline) }) },
  { label: '美食转盘', key: 'wheel', icon: () => h(NIcon, null, { default: () => h(StarOutline) }) },
  { label: '盲盒惊喜', key: 'mystery', icon: () => h(NIcon, null, { default: () => h(GiftOutline) }) },
  { label: '周计划', key: 'weekly-plan', icon: () => h(NIcon, null, { default: () => h(CalendarOutline) }) },
  { label: '用餐记录', key: 'records', icon: () => h(NIcon, null, { default: () => h(TimeOutline) }) },
  { label: '成就系统', key: 'achievements', icon: () => h(NIcon, null, { default: () => h(TrophyOutline) }) },
  { label: '数据统计', key: 'stats', icon: () => h(NIcon, null, { default: () => h(StatsChartOutline) }) }
]

const activeKey = computed(() => route.name as string)

function handleMenuUpdate(key: string) {
  router.push({ name: key })
  showMobileDrawer.value = false
}

const today = new Date()
const dateStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`
const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
const weekday = weekdays[today.getDay()]
const greeting = (() => {
  const h = today.getHours()
  if (h < 6) return '夜深了'
  if (h < 11) return '早上好'
  if (h < 14) return '中午好'
  if (h < 18) return '下午好'
  return '晚上好'
})()
</script>

<template>
  <NLayout has-sider style="height: 100vh">
    <NLayoutSider
      v-if="!isMobile"
      bordered
      collapse-mode="width"
      :collapsed-width="64"
      :width="220"
      :collapsed="collapsed"
      show-trigger
      @collapse="collapsed = true"
      @expand="collapsed = false"
    >
      <div class="logo" :class="{ collapsed }">
        <span v-if="!collapsed">🍽️ 食光</span>
        <span v-else>🍽️</span>
      </div>
      <NMenu
        :collapsed="collapsed"
        :collapsed-width="64"
        :collapsed-icon-size="22"
        :options="menuOptions"
        :value="activeKey"
        @update:value="handleMenuUpdate"
      />
    </NLayoutSider>

    <NLayout>
      <NLayoutHeader bordered class="top-header">
        <NSpace align="center" :wrap="false">
          <NButton
            v-if="isMobile"
            quaternary
            circle
            @click="showMobileDrawer = true"
          >
            <template #icon><NIcon :component="MenuOutline" /></template>
          </NButton>
          <div v-if="isMobile" class="brand-mobile">🍽️ 食光</div>
        </NSpace>
        <NSpace align="center" :wrap="false" class="header-right">
          <NTag :bordered="false" type="info" size="small">{{ dateStr }} {{ weekday }}</NTag>
          <span class="greeting">{{ greeting }} 👋</span>
        </NSpace>
      </NLayoutHeader>

      <NLayoutContent class="content">
        <router-view />
      </NLayoutContent>
    </NLayout>

    <NDrawer v-if="isMobile" v-model:show="showMobileDrawer" :width="240" placement="left">
      <NDrawerContent closable>
        <div class="logo mobile">🍽️ 食光</div>
        <NMenu
          :options="menuOptions"
          :value="activeKey"
          @update:value="handleMenuUpdate"
        />
      </NDrawerContent>
    </NDrawer>
  </NLayout>
</template>

<style scoped>
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 600;
  color: #333;
  border-bottom: 1px solid #eee;
}

.logo.collapsed {
  font-size: 22px;
}

.logo.mobile {
  border-bottom: 1px solid #eee;
  margin-bottom: 8px;
}

.top-header {
  height: 56px;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
}

.brand-mobile {
  font-size: 18px;
  font-weight: 600;
  margin-left: 8px;
}

.header-right {
  gap: 12px;
}

.greeting {
  font-size: 14px;
  color: #666;
}

.content {
  height: calc(100vh - 56px);
  overflow-y: auto;
  background: #fafafa;
}

@media (max-width: 640px) {
  .greeting {
    display: none;
  }
  .top-header {
    padding: 0 12px;
  }
}
</style>
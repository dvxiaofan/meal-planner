<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { NLayout, NLayoutSider, NLayoutContent, NMenu, NIcon } from 'naive-ui'
import type { MenuOption } from 'naive-ui'
import {
  HomeOutline,
  RestaurantOutline,
  StarOutline,
  TimeOutline,
  CalendarOutline,
  TrophyOutline,
  StatsChartOutline,
  ColorWandOutline
} from '@vicons/ionicons5'

const router = useRouter()
const route = useRoute()
const collapsed = ref(false)

const menuOptions: MenuOption[] = [
  {
    label: '首页',
    key: 'home',
    icon: () => h(NIcon, null, { default: () => h(HomeOutline) })
  },
  {
    label: '菜品管理',
    key: 'dishes',
    icon: () => h(NIcon, null, { default: () => h(RestaurantOutline) })
  },
  {
    label: '智能推荐',
    key: 'recommend',
    icon: () => h(NIcon, null, { default: () => h(ColorWandOutline) })
  },
  {
    label: '美食转盘',
    key: 'wheel',
    icon: () => h(NIcon, null, { default: () => h(StarOutline) })
  },
  {
    label: '周计划',
    key: 'weekly-plan',
    icon: () => h(NIcon, null, { default: () => h(CalendarOutline) })
  },
  {
    label: '用餐记录',
    key: 'records',
    icon: () => h(NIcon, null, { default: () => h(TimeOutline) })
  },
  {
    label: '成就系统',
    key: 'achievements',
    icon: () => h(NIcon, null, { default: () => h(TrophyOutline) })
  },
  {
    label: '数据统计',
    key: 'stats',
    icon: () => h(NIcon, null, { default: () => h(StatsChartOutline) })
  }
]

const activeKey = computed(() => {
  return route.name as string
})

function handleMenuUpdate(key: string) {
  router.push({ name: key })
}

// 需要导入h函数
import { h } from 'vue'
</script>

<template>
  <NLayout has-sider style="height: 100vh">
    <NLayoutSider
      bordered
      collapse-mode="width"
      :collapsed-width="64"
      :width="240"
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
    <NLayoutContent>
      <router-view />
    </NLayoutContent>
  </NLayout>
</template>

<style scoped>
.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 600;
  color: #333;
  border-bottom: 1px solid #eee;
}

.logo.collapsed {
  font-size: 24px;
}
</style>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { NCard, NGrid, NGi, NStatistic, NSpin, NSpace, NTag } from 'naive-ui'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, BarChart, LineChart } from 'echarts/charts'
import {
  TitleComponent, TooltipComponent, LegendComponent, GridComponent
} from 'echarts/components'
import { useStatsStore } from '@/stores'
import { statsApi } from '@/api/dish'

use([
  CanvasRenderer,
  PieChart, BarChart, LineChart,
  TitleComponent, TooltipComponent, LegendComponent, GridComponent
])

const statsStore = useStatsStore()
const loading = ref(false)

interface Breakdown {
  by_taste: Record<string, number>
  by_category_records: Record<string, number>
  weekly: Array<{ label: string; count: number }>
  category_trend: { dates: string[]; series: Array<{ name: string; data: number[] }> }
}
const breakdown = ref<Breakdown | null>(null)

const categoryOption = computed(() => {
  const dist = statsStore.dashboard?.category_distribution ?? {}
  return {
    tooltip: { trigger: 'item' },
    legend: { bottom: 0, type: 'scroll' },
    series: [
      {
        type: 'pie',
        radius: ['45%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
        label: { show: true, formatter: '{b}: {c} ({d}%)' },
        data: Object.entries(dist).map(([name, value]) => ({ name, value }))
      }
    ]
  }
})

const topDishesOption = computed(() => {
  const list = statsStore.dashboard?.top_dishes ?? []
  return {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 80, right: 20, top: 20, bottom: 30 },
    xAxis: { type: 'value', minInterval: 1 },
    yAxis: { type: 'category', data: list.map(d => d.name).reverse() },
    series: [
      {
        type: 'bar',
        data: list.map(d => d.count).reverse(),
        itemStyle: { color: '#18a058', borderRadius: [0, 4, 4, 0] },
        label: { show: true, position: 'right' }
      }
    ]
  }
})

const trendOption = computed(() => {
  const series = statsStore.trend ?? []
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: 40, right: 20, top: 20, bottom: 40 },
    xAxis: {
      type: 'category',
      data: series.map(s => s.date.slice(5)),
      axisLabel: { rotate: 0 }
    },
    yAxis: { type: 'value', minInterval: 1 },
    series: [
      {
        type: 'line',
        data: series.map(s => s.count),
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { color: '#18a058', width: 2 },
        itemStyle: { color: '#18a058' },
        areaStyle: {
          color: {
            type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(24, 160, 88, 0.4)' },
              { offset: 1, color: 'rgba(24, 160, 88, 0.05)' }
            ]
          }
        }
      }
    ]
  }
})

const tasteOption = computed(() => {
  const data = breakdown.value?.by_taste ?? {}
  return {
    tooltip: { trigger: 'item' },
    legend: { bottom: 0, type: 'scroll' },
    series: [{
      type: 'pie',
      radius: ['40%', '65%'],
      itemStyle: { borderRadius: 4, borderColor: '#fff', borderWidth: 2 },
      label: { show: true, formatter: '{b}: {c}' },
      data: Object.entries(data).map(([name, value]) => ({ name, value }))
    }]
  }
})

const weeklyOption = computed(() => {
  const wk = breakdown.value?.weekly ?? []
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: 50, right: 20, top: 20, bottom: 30 },
    xAxis: { type: 'category', data: wk.map(w => w.label) },
    yAxis: { type: 'value', minInterval: 1 },
    series: [{
      type: 'bar',
      data: wk.map(w => w.count),
      itemStyle: { color: '#2080f0', borderRadius: [4, 4, 0, 0] },
      label: { show: true, position: 'top' }
    }]
  }
})

const categoryTrendOption = computed(() => {
  const trend = breakdown.value?.category_trend
  if (!trend) return {}
  return {
    tooltip: { trigger: 'axis' },
    legend: { bottom: 0, type: 'scroll' },
    grid: { left: 40, right: 20, top: 20, bottom: 50 },
    xAxis: { type: 'category', data: trend.dates, axisLabel: { rotate: 0 } },
    yAxis: { type: 'value', minInterval: 1 },
    series: trend.series.map(s => ({
      name: s.name,
      type: 'line',
      smooth: true,
      data: s.data
    }))
  }
})

onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([
      statsStore.fetchDashboardStats(),
      statsStore.fetchTrend(14),
      statsApi.getBreakdown().then(d => { breakdown.value = d as Breakdown })
    ])
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="page-container">
    <h1 class="page-title">数据统计</h1>

    <NSpace vertical :size="16">
      <NGrid :cols="4" :x-gap="16">
        <NGi>
          <NCard>
            <NStatistic label="菜品总数" :value="statsStore.dashboard?.total_dishes || 0" />
          </NCard>
        </NGi>
        <NGi>
          <NCard>
            <NStatistic label="用餐记录" :value="statsStore.dashboard?.total_records || 0" />
          </NCard>
        </NGi>
        <NGi>
          <NCard>
            <NStatistic label="已收藏菜品">
              <NSpace align="center">
                <span>{{ statsStore.dashboard?.top_dishes?.length || 0 }}</span>
                <NTag size="small" type="error">★</NTag>
              </NSpace>
            </NStatistic>
          </NCard>
        </NGi>
        <NGi>
          <NCard>
            <NStatistic label="今日已记录">
              {{ (statsStore.trend?.[statsStore.trend.length - 1]?.count) || 0 }}
              <span style="font-size: 12px; color: #999; margin-left: 4px">餐</span>
            </NStatistic>
          </NCard>
        </NGi>
      </NGrid>

      <NSpin :show="loading">
        <NGrid :cols="2" :x-gap="16">
          <NGi>
            <NCard title="近 14 天用餐趋势">
              <VChart :option="trendOption" autoresize style="height: 280px" />
            </NCard>
          </NGi>
          <NGi>
            <NCard title="菜品分类（库内）">
              <VChart :option="categoryOption" autoresize style="height: 280px" />
            </NCard>
          </NGi>
        </NGrid>

        <NGrid :cols="2" :x-gap="16" style="margin-top: 16px">
          <NGi>
            <NCard title="口味偏好（已吃过的菜）">
              <VChart :option="tasteOption" autoresize style="height: 280px" />
            </NCard>
          </NGi>
          <NGi>
            <NCard title="近 4 周对比">
              <VChart :option="weeklyOption" autoresize style="height: 280px" />
            </NCard>
          </NGi>
        </NGrid>

        <NCard title="近 30 天分类趋势" style="margin-top: 16px">
          <VChart :option="categoryTrendOption" autoresize style="height: 320px" />
        </NCard>

        <NCard title="热门菜品 Top 10" style="margin-top: 16px">
          <VChart
            v-if="statsStore.dashboard?.top_dishes?.length"
            :option="topDishesOption"
            autoresize
            style="height: 360px"
          />
          <div v-else style="text-align: center; color: #999; padding: 40px">
            暂无数据，开始记录第一餐吧
          </div>
        </NCard>
      </NSpin>
    </NSpace>
  </div>
</template>
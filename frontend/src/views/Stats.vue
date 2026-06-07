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

use([
  CanvasRenderer,
  PieChart, BarChart, LineChart,
  TitleComponent, TooltipComponent, LegendComponent, GridComponent
])

const statsStore = useStatsStore()
const loading = ref(false)

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
      data: series.map(s => s.date.slice(5)), // MM-DD
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

onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([
      statsStore.fetchDashboardStats(),
      statsStore.fetchTrend(14)
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
      <!-- 顶部统计 -->
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
        <!-- 趋势 + 分类分布 -->
        <NGrid :cols="2" :x-gap="16">
          <NGi>
            <NCard title="近 14 天用餐趋势">
              <VChart :option="trendOption" autoresize style="height: 280px" />
            </NCard>
          </NGi>
          <NGi>
            <NCard title="菜品分类分布">
              <VChart :option="categoryOption" autoresize style="height: 280px" />
            </NCard>
          </NGi>
        </NGrid>

        <!-- 热门菜品 -->
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
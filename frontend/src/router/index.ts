import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: MainLayout,
      children: [
        {
          path: '',
          name: 'home',
          component: () => import('@/views/Home.vue'),
          meta: { title: '首页' }
        },
        {
          path: 'dishes',
          name: 'dishes',
          component: () => import('@/views/Dishes.vue'),
          meta: { title: '菜品管理' }
        },
        {
          path: 'dishes/:id',
          name: 'dish-detail',
          component: () => import('@/views/DishDetail.vue'),
          meta: { title: '菜品详情' }
        },
        {
          path: 'recommend',
          name: 'recommend',
          component: () => import('@/views/Recommend.vue'),
          meta: { title: '智能推荐' }
        },
        {
          path: 'wheel',
          name: 'wheel',
          component: () => import('@/views/Wheel.vue'),
          meta: { title: '美食转盘' }
        },
        {
          path: 'mystery',
          name: 'mystery',
          component: () => import('@/views/Mystery.vue'),
          meta: { title: '盲盒惊喜' }
        },
        {
          path: 'weekly-plan',
          name: 'weekly-plan',
          component: () => import('@/views/WeeklyPlan.vue'),
          meta: { title: '周计划' }
        },
        {
          path: 'records',
          name: 'records',
          component: () => import('@/views/Records.vue'),
          meta: { title: '用餐记录' }
        },
        {
          path: 'achievements',
          name: 'achievements',
          component: () => import('@/views/Achievements.vue'),
          meta: { title: '成就系统' }
        },
        {
          path: 'stats',
          name: 'stats',
          component: () => import('@/views/Stats.vue'),
          meta: { title: '数据统计' }
        }
      ]
    }
  ]
})

export default router

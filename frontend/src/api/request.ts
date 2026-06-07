import axios from 'axios'
import type { AxiosInstance, AxiosResponse } from 'axios'
import { notify } from '@/utils/notify'

const request: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse) => {
    return response.data
  },
  (error) => {
    // 提取后端 detail 或网络错误信息
    const detail = error.response?.data?.detail
    const text = typeof detail === 'string'
      ? detail
      : error.message || '请求失败'
    // 网络层异常一律弹通知；业务层可选择不弹（catch 中显式处理）
    if (!error.config?.__silent) {
      notify.error(text)
    }
    return Promise.reject(error)
  }
)

// 业务层可临时静默：request.__silent = true; await api.x()
;(request as any).__silent = false

export default request

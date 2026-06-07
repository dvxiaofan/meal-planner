import { createDiscreteApi } from 'naive-ui'

// 在组件外也能用的全局消息工具（基于 Naive UI discrete API）
const { message, notification } = createDiscreteApi(['message', 'notification'])

export const notify = {
  success: (text: string) => message.success(text),
  error: (text: string) => message.error(text),
  info: (text: string) => message.info(text),
  warning: (text: string) => message.warning(text),
  // 用于需要更详细说明的错误（如后端返回的 detail 字段）
  notifyError: (title: string, content?: string) => {
    notification.error({ title, content, duration: 5000 })
  }
}
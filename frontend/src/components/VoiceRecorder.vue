<script setup lang="ts">
import { ref, computed, onBeforeUnmount } from 'vue'
import { NCard, NButton, NSpace, NTag, NSpin, NIcon, useMessage } from 'naive-ui'
import { MicOutline, MicOffOutline, CloseCircle } from '@vicons/ionicons5'
import { useDishStore } from '@/stores'
import { recordApi } from '@/api'
import RecordMealModal from './RecordMealModal.vue'
import type { Dish } from '@/types'

const message = useMessage()
const dishStore = useDishStore()

const listening = ref(false)
const transcript = ref('')
const interim = ref('')
const error = ref<string | null>(null)
const showResult = ref(false)
const matchedDish = ref<Dish | null>(null)
const showRecordModal = ref(false)

// Web Speech API
const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
const recognition = SpeechRecognition ? new SpeechRecognition() : null

if (recognition) {
  recognition.lang = 'zh-CN'
  recognition.continuous = false
  recognition.interimResults = true
  recognition.maxAlternatives = 3

  recognition.onresult = (e: any) => {
    let finalText = ''
    let interimText = ''
    for (let i = e.resultIndex; i < e.results.length; i++) {
      const r = e.results[i]
      if (r.isFinal) finalText += r[0].transcript
      else interimText += r[0].transcript
    }
    if (finalText) transcript.value += finalText
    interim.value = interimText
  }

  recognition.onerror = (e: any) => {
    error.value = `识别错误: ${e.error || '未知'}`
    listening.value = false
  }

  recognition.onend = () => {
    listening.value = false
    if (transcript.value) {
      handleTranscript(transcript.value)
    }
  }
}

function start() {
  if (!recognition) {
    message.error('当前浏览器不支持语音识别')
    return
  }
  if (dishStore.dishes.length === 0) {
    dishStore.fetchDishes()
  }
  transcript.value = ''
  interim.value = ''
  error.value = null
  matchedDish.value = null
  showResult.value = true
  try {
    recognition.start()
    listening.value = true
  } catch (e) {
    error.value = '无法启动语音识别'
    listening.value = false
  }
}

function stop() {
  if (recognition && listening.value) {
    recognition.stop()
  }
}

function close() {
  stop()
  showResult.value = false
  transcript.value = ''
  interim.value = ''
}

onBeforeUnmount(() => {
  if (recognition) {
    try { recognition.stop() } catch {}
  }
})

// 简单匹配算法：把 transcript 与菜品名做包含/相似度匹配
function matchDish(text: string): Dish | null {
  if (!text) return null
  const clean = text.replace(/[，。！？、,.!?\s]/g, '').trim()
  if (!clean) return null
  // 完全包含
  for (const d of dishStore.dishes) {
    if (clean.includes(d.name) || d.name.includes(clean)) {
      return d
    }
  }
  // 单字匹配：取菜品名第一个字
  for (const d of dishStore.dishes) {
    if (clean.includes(d.name[0]) && d.name.length <= 4) {
      return d
    }
  }
  return null
}

const matchResult = computed(() => {
  if (!transcript.value) return null
  return matchDish(transcript.value)
})

function handleTranscript(text: string) {
  const dish = matchDish(text)
  matchedDish.value = dish
  if (!dish) {
    error.value = `没有匹配到菜品："${text}"`
  }
}

function confirmAndRecord() {
  if (matchedDish.value) {
    showRecordModal.value = true
  }
}

async function createRecordDirect() {
  if (!matchedDish.value) return
  try {
    const now = new Date()
    const h = now.getHours()
    await recordApi.createRecord({
      dish_id: matchedDish.value.id,
      meal_type: h < 15 ? 'lunch' : 'dinner',
      record_date: now.toISOString()
    })
    message.success(`已记录：${matchedDish.value.name}`)
    close()
  } catch {
    // 拦截器已处理
  }
}
</script>

<template>
  <!-- 悬浮按钮 -->
  <div class="voice-fab" @click="start" v-if="!showResult">
    <NIcon :component="MicOutline" :size="24" />
  </div>

  <!-- 录音弹层 -->
  <div v-if="showResult" class="voice-overlay" @click.self="close">
    <NCard class="voice-card">
      <template #header>
        <NSpace align="center">
          <NIcon :component="MicOutline" :size="20" />
          <span>语音记录</span>
          <NButton quaternary circle size="small" style="margin-left: auto" @click="close">
            <template #icon><NIcon :component="CloseCircle" /></template>
          </NButton>
        </NSpace>
      </template>

      <div class="voice-status">
        <div v-if="listening" class="listening-pulse">
          <div class="pulse-ring"></div>
          <div class="pulse-ring delay"></div>
          <NIcon :component="MicOutline" :size="32" class="mic-icon" />
        </div>
        <div v-else-if="error" class="status-error">
          {{ error }}
        </div>
        <div v-else-if="transcript" class="status-done">
          ✅ 识别完成
        </div>
        <div v-else class="status-ready">
          点击开始录音
        </div>
      </div>

      <div class="transcript-box">
        <div v-if="transcript" class="transcript-final">
          {{ transcript }}
        </div>
        <div v-if="interim" class="transcript-interim">{{ interim }}</div>
        <div v-if="!transcript && !interim" class="transcript-empty">
          试试说："我刚吃了番茄炒蛋" 或 "今天中午吃红烧肉"
        </div>
      </div>

      <div v-if="matchResult" class="match-result">
        <NTag type="success">匹配到：{{ matchResult.name }}</NTag>
      </div>

      <template #action>
        <NSpace justify="center">
          <NButton
            v-if="!listening"
            type="primary"
            @click="start"
            :disabled="!recognition"
          >
            <template #icon><NIcon :component="MicOutline" /></template>
            {{ transcript ? '重新录音' : '开始录音' }}
          </NButton>
          <NButton v-else type="error" @click="stop">
            <template #icon><NIcon :component="MicOffOutline" /></template>
            停止
          </NButton>
          <NButton
            v-if="matchedDish && !listening"
            type="success"
            @click="createRecordDirect"
          >
            ✓ 快速记录
          </NButton>
          <NButton
            v-if="matchedDish && !listening"
            @click="confirmAndRecord"
          >
            详细记录
          </NButton>
        </NSpace>
      </template>
    </NCard>
  </div>

  <RecordMealModal v-model:show="showRecordModal" :dish="matchedDish" />
</template>

<style scoped>
.voice-fab {
  position: fixed;
  right: 24px;
  bottom: 80px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #18a058, #0e7c45);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6px 20px rgba(24, 160, 88, 0.3);
  cursor: pointer;
  z-index: 999;
  transition: transform 0.2s, box-shadow 0.2s;
}

.voice-fab:hover {
  transform: scale(1.1);
  box-shadow: 0 8px 24px rgba(24, 160, 88, 0.4);
}

.voice-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 16px;
}

.voice-card {
  width: 480px;
  max-width: 100%;
}

.voice-status {
  text-align: center;
  padding: 20px 0;
  min-height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.listening-pulse {
  position: relative;
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mic-icon {
  color: #18a058;
  z-index: 2;
}

.pulse-ring {
  position: absolute;
  inset: 0;
  border: 3px solid #18a058;
  border-radius: 50%;
  animation: pulse-out 1.5s ease-out infinite;
}

.pulse-ring.delay {
  animation-delay: 0.75s;
}

@keyframes pulse-out {
  0% { transform: scale(0.5); opacity: 1; }
  100% { transform: scale(1.5); opacity: 0; }
}

.status-error {
  color: #d03050;
  font-size: 14px;
}

.status-done {
  color: #18a058;
  font-size: 16px;
  font-weight: 500;
}

.status-ready {
  color: #999;
  font-size: 14px;
}

.transcript-box {
  background: #fafafa;
  border-radius: 8px;
  padding: 16px;
  min-height: 80px;
  margin-bottom: 12px;
}

.transcript-final {
  font-size: 18px;
  color: #333;
  font-weight: 500;
  line-height: 1.6;
}

.transcript-interim {
  font-size: 14px;
  color: #999;
  margin-top: 4px;
  line-height: 1.6;
}

.transcript-empty {
  font-size: 13px;
  color: #bbb;
  text-align: center;
  padding: 16px 0;
}

.match-result {
  text-align: center;
  padding: 8px 0;
}
</style>
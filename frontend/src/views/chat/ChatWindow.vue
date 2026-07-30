<script setup lang="ts">
import { ref, nextTick, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { chatApi } from '@/api/chat'
import type { Message } from '@/types'
import ChatStreamRenderer from '@/components/ChatStreamRenderer.vue'

const route = useRoute()
const messages = ref<Message[]>([])
const inputText = ref('')
const thinkingEnabled = ref(false)
const searchEnabled = ref(false)
const loading = ref(false)
const messagesContainer = ref<HTMLElement>()

async function loadMessages() {
  const routeId = route.params.routeId as string
  if (!routeId) return
  try {
    const res = await chatApi.getMessages(routeId)
    messages.value = res.data
    await nextTick()
    scrollToBottom()
  } catch { /* ignore */ }
}

function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text || loading.value) return
  const routeId = route.params.routeId as string

  messages.value.push({
    id: '', role: 'user', content: text,
    metadata: { thinking: thinkingEnabled.value, search: searchEnabled.value },
    tokens_used: 0, created_at: new Date().toISOString(),
  })
  inputText.value = ''
  loading.value = true

  const assistantMsg: Message = {
    id: '', role: 'assistant', content: '',
    metadata: {}, tokens_used: 0, created_at: new Date().toISOString(),
  }
  messages.value.push(assistantMsg)

  const token = localStorage.getItem('access_token')
  const baseUrl = import.meta.env.VITE_API_BASE_URL

  try {
    const response = await fetch(`${baseUrl}/chat/conversations/${routeId}/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        content: text,
        metadata: { thinking: thinkingEnabled.value, search: searchEnabled.value },
      }),
    })

    const reader = response.body?.getReader()
    const decoder = new TextDecoder()
    if (!reader) return

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      const chunk = decoder.decode(value, { stream: true })
      const lines = chunk.split('\n')
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          if (data === '[DONE]') continue
          try {
            const parsed = JSON.parse(data)
            assistantMsg.content += parsed.content || ''
            await nextTick()
            scrollToBottom()
          } catch { /* ignore */ }
        }
      }
    }
  } finally {
    loading.value = false
    loadMessages()
  }
}

watch(() => route.params.routeId, () => {
  messages.value = []
  loadMessages()
})

onMounted(loadMessages)
</script>

<template>
  <div class="flex flex-col h-full">
    <div ref="messagesContainer" class="flex-1 overflow-y-auto p-4 space-y-4">
      <ChatStreamRenderer
        v-for="(msg, idx) in messages"
        :key="idx"
        :message="msg"
      />
    </div>
    <footer class="border-t p-4">
      <div class="flex items-center gap-3 mb-2">
        <el-switch v-model="thinkingEnabled" size="small" active-text="深度思考" />
        <el-switch v-model="searchEnabled" size="small" active-text="联网搜索" />
        <el-button size="small">+ 文件上传</el-button>
      </div>
      <div class="flex gap-2">
        <el-input
          v-model="inputText"
          type="textarea"
          :rows="2"
          placeholder="输入消息..."
          @keydown.enter.exact.prevent="sendMessage"
        />
        <el-button type="primary" :loading="loading" @click="sendMessage">发送</el-button>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { chatApi } from '@/api/chat'
import type { Conversation } from '@/types'
import GlobalUserWidget from '@/components/GlobalUserWidget.vue'

const router = useRouter()
const conversations = ref<Conversation[]>([])
const loading = ref(false)

async function loadConversations() {
  loading.value = true
  try {
    const res = await chatApi.getConversations()
    conversations.value = res.data
  } finally {
    loading.value = false
  }
}

async function createNewChat() {
  try {
    const res = await chatApi.createConversation()
    conversations.value.unshift(res.data)
    router.push(`/chat/${res.data.route_id}`)
  } catch { /* ignore */ }
}

onMounted(loadConversations)
</script>

<template>
  <div class="flex h-screen">
    <aside class="w-64 bg-gray-50 border-r flex flex-col">
      <div class="p-4">
        <el-button type="primary" class="w-full" @click="createNewChat">新建对话</el-button>
      </div>
      <div class="flex-1 overflow-y-auto px-2">
        <div
          v-for="conv in conversations"
          :key="conv.id"
          class="p-3 rounded-lg cursor-pointer hover:bg-gray-200 text-sm truncate"
          :class="{ 'bg-gray-200': $route.params.routeId === conv.route_id }"
          @click="router.push(`/chat/${conv.route_id}`)"
        >
          {{ conv.title }}
        </div>
      </div>
    </aside>
    <main class="flex-1 flex flex-col">
      <header class="h-14 border-b flex items-center justify-end px-4">
        <router-link to="/api" class="text-sm text-blue-500 hover:underline">API 服务</router-link>
      </header>
      <div class="flex-1 overflow-hidden">
        <router-view />
      </div>
    </main>
    <GlobalUserWidget />
  </div>
</template>

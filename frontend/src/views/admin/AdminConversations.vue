<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { adminApi } from '@/api/admin'
import type { AdminConversation, AdminMessage } from '@/types'

const conversations = ref<AdminConversation[]>([])
const selectedMessages = ref<AdminMessage[]>([])
const dialogVisible = ref(false)
const selectedTitle = ref('')

async function loadConversations() {
  try {
    const res = await adminApi.getConversations()
    conversations.value = res.data
  } catch { /* ignore */ }
}

async function viewMessages(conv: AdminConversation) {
  selectedTitle.value = conv.title
  try {
    const res = await adminApi.getConversationMessages(conv.id)
    selectedMessages.value = res.data
    dialogVisible.value = true
  } catch { /* ignore */ }
}

onMounted(loadConversations)
</script>

<template>
  <div>
    <h2 class="text-xl font-bold mb-4">对话管理</h2>
    <el-table :data="conversations" style="width: 100%">
      <el-table-column prop="title" label="标题" />
      <el-table-column prop="username" label="用户" width="120" />
      <el-table-column prop="phone" label="手机号" width="140" />
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button size="small" @click="viewMessages(row)">查看</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="selectedTitle" width="700px">
      <div class="max-h-96 overflow-y-auto space-y-3">
        <div
          v-for="msg in selectedMessages"
          :key="msg.id"
          class="p-3 rounded-lg"
          :class="msg.role === 'user' ? 'bg-blue-50 ml-8' : 'bg-gray-50 mr-8'"
        >
          <div class="text-xs text-gray-400 mb-1">
            {{ msg.role === 'user' ? '用户' : 'AI' }} · {{ msg.tokens_used }} tokens
          </div>
          <div class="text-sm whitespace-pre-wrap">{{ msg.content }}</div>
        </div>
        <div v-if="selectedMessages.length === 0" class="text-center text-gray-400 py-8">
          暂无消息
        </div>
      </div>
    </el-dialog>
  </div>
</template>

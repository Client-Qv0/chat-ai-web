<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { adminApi } from '@/api/admin'
import type { AdminStats } from '@/types'

const stats = ref<AdminStats>({
  total_users: 0, total_conversations: 0,
  total_messages: 0, total_tokens: 0,
})

onMounted(async () => {
  try {
    const res = await adminApi.getStats()
    stats.value = res.data
  } catch { /* ignore */ }
})
</script>

<template>
  <div>
    <h2 class="text-xl font-bold mb-6">系统概览</h2>
    <div class="grid grid-cols-4 gap-4">
      <el-card shadow="hover">
        <el-statistic title="用户总数" :value="stats.total_users" />
      </el-card>
      <el-card shadow="hover">
        <el-statistic title="对话总数" :value="stats.total_conversations" />
      </el-card>
      <el-card shadow="hover">
        <el-statistic title="消息总数" :value="stats.total_messages" />
      </el-card>
      <el-card shadow="hover">
        <el-statistic title="Token 消耗" :value="stats.total_tokens" />
      </el-card>
    </div>
  </div>
</template>

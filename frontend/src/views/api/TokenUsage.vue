<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { tokenUsageApi } from '@/api/token-usage'
import type { TokenUsageSummary, DailyUsage } from '@/types'

const summary = ref<TokenUsageSummary>({ total_tokens: 0, today_tokens: 0 })
const dailyData = ref<DailyUsage[]>([])
const days = ref(7)

async function load() {
  const [s, d] = await Promise.all([
    tokenUsageApi.getSummary(),
    tokenUsageApi.getDaily(days.value),
  ])
  summary.value = s.data
  dailyData.value = d.data
}

onMounted(load)
</script>

<template>
  <div>
    <h2 class="text-xl font-bold mb-4">Token 用量</h2>
    <div class="grid grid-cols-3 gap-4 mb-6">
      <el-statistic title="总消耗" :value="summary.total_tokens" />
      <el-statistic title="今日消耗" :value="summary.today_tokens" />
      <el-statistic title="剩余可用" value="不限" />
    </div>
    <div class="flex items-center gap-2 mb-4">
      <span class="text-sm text-gray-500">显示近</span>
      <el-radio-group v-model="days" size="small" @change="load">
        <el-radio-button :value="7">7天</el-radio-button>
        <el-radio-button :value="30">30天</el-radio-button>
      </el-radio-group>
    </div>
    <div class="bg-white rounded-lg p-4">
      <div v-if="dailyData.length === 0" class="text-gray-400 text-center py-8">暂无数据</div>
      <table v-else class="w-full text-sm">
        <thead>
          <tr class="border-b">
            <th class="text-left py-2">日期</th>
            <th class="text-right py-2">输入</th>
            <th class="text-right py-2">输出</th>
            <th class="text-right py-2">合计</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="d in dailyData" :key="d.date" class="border-b">
            <td class="py-2">{{ d.date }}</td>
            <td class="text-right">{{ d.prompt_tokens }}</td>
            <td class="text-right">{{ d.completion_tokens }}</td>
            <td class="text-right font-bold">{{ d.total_tokens }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

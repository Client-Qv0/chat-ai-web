<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiKeysApi } from '@/api/api-keys'
import type { ApiKey } from '@/types'
import { ElMessage, ElMessageBox } from 'element-plus'

const keys = ref<ApiKey[]>([])

async function loadKeys() {
  const res = await apiKeysApi.list()
  keys.value = res.data
}

async function generateKey() {
  try {
    const res = await apiKeysApi.generate()
    ElMessageBox.alert(`新密钥（仅显示一次，请复制保存）：\n${res.data.full_key}`, '密钥已生成', {
      confirmButtonText: '已复制',
    })
    await loadKeys()
  } catch { ElMessage.error('生成失败') }
}

async function revokeKey(id: string) {
  try {
    await ElMessageBox.confirm('确定要禁用此密钥吗？', '确认', { type: 'warning' })
    await apiKeysApi.revoke(id)
    ElMessage.success('已禁用')
    await loadKeys()
  } catch { /* cancelled */ }
}

onMounted(loadKeys)
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl font-bold">API Key 管理</h2>
      <el-button type="primary" @click="generateKey">生成新 Key</el-button>
    </div>
    <el-table :data="keys" style="width: 100%">
      <el-table-column prop="key_prefix" label="Key" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'danger'" size="small">
            {{ row.status === 'active' ? '可用' : '已禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button
            v-if="row.status === 'active'"
            size="small"
            type="danger"
            @click="revokeKey(row.id)"
          >
            禁用
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { adminApi } from '@/api/admin'
import type { AdminUser } from '@/types'
import { ElMessage, ElMessageBox } from 'element-plus'

const users = ref<AdminUser[]>([])

async function loadUsers() {
  try {
    const res = await adminApi.getUsers()
    users.value = res.data
  } catch { /* ignore */ }
}

async function toggleRole(user: AdminUser) {
  const newRole = user.role === 'admin' ? 'user' : 'admin'
  try {
    await ElMessageBox.confirm(
      `确定要将 ${user.username} 的角色改为 ${newRole === 'admin' ? '管理员' : '普通用户'} 吗？`,
      '确认操作',
      { type: 'warning' }
    )
    await adminApi.updateUserRole(user.id, newRole)
    ElMessage.success('角色已更新')
    await loadUsers()
  } catch { /* cancelled */ }
}

onMounted(loadUsers)
</script>

<template>
  <div>
    <h2 class="text-xl font-bold mb-4">用户管理</h2>
    <el-table :data="users" style="width: 100%">
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="phone" label="手机号" />
      <el-table-column prop="role" label="角色" width="120">
        <template #default="{ row }">
          <el-tag :type="row.role === 'admin' ? 'warning' : 'info'" size="small">
            {{ row.role === 'admin' ? '管理员' : '普通用户' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="注册时间" width="180" />
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button size="small" @click="toggleRole(row)">
            {{ row.role === 'admin' ? '取消管理' : '设为管理' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

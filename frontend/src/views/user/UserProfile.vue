<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api/auth'
import { ElMessage } from 'element-plus'

const auth = useAuthStore()
const username = ref('')
const saving = ref(false)

const passwordForm = ref({ old_password: '', new_password: '', confirm: '' })
const changingPwd = ref(false)

onMounted(async () => {
  await auth.loadUser()
  username.value = auth.user?.username || ''
})

async function updateProfile() {
  saving.value = true
  try {
    const res = await authApi.updateProfile({ username: username.value })
    auth.user = res.data
    localStorage.setItem('user_info', JSON.stringify(res.data))
    ElMessage.success('修改成功')
  } catch { ElMessage.error('修改失败') }
  finally { saving.value = false }
}

async function changePassword() {
  if (passwordForm.value.new_password !== passwordForm.value.confirm) {
    ElMessage.error('两次密码不一致')
    return
  }
  changingPwd.value = true
  try {
    await authApi.changePassword({
      old_password: passwordForm.value.old_password,
      new_password: passwordForm.value.new_password,
    })
    ElMessage.success('密码修改成功')
    passwordForm.value = { old_password: '', new_password: '', confirm: '' }
  } catch { ElMessage.error('密码修改失败') }
  finally { changingPwd.value = false }
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex justify-center py-12">
    <div class="w-full max-w-lg space-y-6">
      <div class="bg-white rounded-2xl shadow p-6">
        <h2 class="text-lg font-bold mb-4">基本信息</h2>
        <el-form label-position="top">
          <el-form-item label="用户名">
            <el-input v-model="username" />
          </el-form-item>
          <el-form-item label="手机号">
            <el-input :model-value="auth.user?.phone" disabled />
          </el-form-item>
          <el-form-item label="注册时间">
            <el-input :model-value="auth.user?.created_at" disabled />
          </el-form-item>
          <el-button type="primary" :loading="saving" @click="updateProfile">保存</el-button>
        </el-form>
      </div>

      <div class="bg-white rounded-2xl shadow p-6">
        <h2 class="text-lg font-bold mb-4">安全设置</h2>
        <el-form label-position="top">
          <el-form-item label="原密码">
            <el-input v-model="passwordForm.old_password" type="password" show-password />
          </el-form-item>
          <el-form-item label="新密码">
            <el-input v-model="passwordForm.new_password" type="password" show-password />
          </el-form-item>
          <el-form-item label="确认新密码">
            <el-input v-model="passwordForm.confirm" type="password" show-password />
          </el-form-item>
          <el-button type="primary" :loading="changingPwd" @click="changePassword">修改密码</el-button>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({ username: '', phone: '', password: '', confirmPassword: '' })
const loading = ref(false)
const error = ref('')

async function handleRegister() {
  if (form.value.password !== form.value.confirmPassword) {
    error.value = '两次密码不一致'
    return
  }
  loading.value = true
  error.value = ''
  try {
    const res = await authApi.register({
      username: form.value.username,
      phone: form.value.phone,
      password: form.value.password,
    })
    authStore.setAuth(res.data.access_token, res.data.user_info)
    router.push('/chat')
  } catch (e: any) {
    error.value = e.response?.data?.detail || '注册失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="w-full max-w-md bg-white rounded-2xl shadow-lg p-8">
      <h1 class="text-2xl font-bold text-center mb-6">注册</h1>
      <el-form @submit.prevent="handleRegister" label-position="top">
        <el-form-item label="用户名">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" placeholder="至少8位，包含字母和数字" show-password />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input v-model="form.confirmPassword" type="password" placeholder="请再次输入密码" show-password />
        </el-form-item>
        <p v-if="error" class="text-red-500 text-sm mb-3">{{ error }}</p>
        <el-button type="primary" native-type="submit" :loading="loading" class="w-full">注册</el-button>
      </el-form>
      <div class="mt-4 text-center text-sm text-gray-500">
        已有账号？<router-link to="/login" class="text-blue-500 hover:underline">去登录</router-link>
      </div>
    </div>
  </div>
</template>

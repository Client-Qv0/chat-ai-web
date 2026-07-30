<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({ phone: '', password: '' })
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  loading.value = true
  error.value = ''
  try {
    const res = await authApi.login(form.value)
    authStore.setAuth(res.data.access_token, res.data.user_info)
    router.push('/chat')
  } catch (e: any) {
    error.value = e.response?.data?.detail || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="w-full max-w-md bg-white rounded-2xl shadow-lg p-8">
      <h1 class="text-2xl font-bold text-center mb-6">登录</h1>
      <el-form @submit.prevent="handleLogin" label-position="top">
        <el-form-item label="手机号">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <p v-if="error" class="text-red-500 text-sm mb-3">{{ error }}</p>
        <el-button type="primary" native-type="submit" :loading="loading" class="w-full">登录</el-button>
      </el-form>
      <div class="mt-4 text-center text-sm text-gray-500">
        <router-link to="/register" class="text-blue-500 hover:underline">注册</router-link>
        <span class="mx-2">|</span>
        <router-link to="/recovery" class="text-blue-500 hover:underline">忘记密码</router-link>
      </div>
    </div>
  </div>
</template>

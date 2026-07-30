import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import type { UserInfo } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const user = ref<UserInfo | null>(null)

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  function setAuth(newToken: string, userInfo: UserInfo) {
    token.value = newToken
    user.value = userInfo
    localStorage.setItem('access_token', newToken)
    localStorage.setItem('user_info', JSON.stringify(userInfo))
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_info')
  }

  async function loadUser() {
    if (!token.value) return
    try {
      const res = await authApi.getMe()
      user.value = res.data
    } catch {
      logout()
    }
  }

  return { token, user, isLoggedIn, isAdmin, setAuth, logout, loadUser }
})

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const auth = useAuthStore()

const hiddenRoutes = ['/', '/login', '/register', '/admin']
const visible = computed(() => !hiddenRoutes.includes(route.path))

function goProfile() {
  if (auth.user) {
    window.open(`/user/${auth.user.phone}`, '_blank')
  }
}

const initial = computed(() => auth.user?.username?.charAt(0).toUpperCase() || '?')
</script>

<template>
  <div
    v-if="visible"
    class="fixed bottom-4 left-4 bg-white rounded-full shadow-lg px-4 py-2 flex items-center gap-2 cursor-pointer hover:shadow-xl transition-shadow border"
    @click="goProfile"
  >
    <div class="w-8 h-8 rounded-full bg-blue-500 text-white flex items-center justify-center text-sm font-bold">
      {{ initial }}
    </div>
    <span class="text-sm font-medium">{{ auth.user?.username }}</span>
  </div>
</template>

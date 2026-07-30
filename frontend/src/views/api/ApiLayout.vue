<script setup lang="ts">
import { useRoute } from 'vue-router'
import GlobalUserWidget from '@/components/GlobalUserWidget.vue'

const route = useRoute()
</script>

<template>
  <div class="flex h-screen">
    <aside class="w-48 bg-gray-50 border-r p-4">
      <el-menu :default-active="route.path" router>
        <el-menu-item index="/api/index">首次调用文档</el-menu-item>
        <el-menu-item index="/api/token">Token 用量</el-menu-item>
        <el-menu-item index="/api/key">API Key 管理</el-menu-item>
      </el-menu>
    </aside>
    <main class="flex-1 flex flex-col">
      <header class="h-14 border-b flex items-center justify-end px-4">
        <router-link to="/chat" class="text-sm text-blue-500 hover:underline">在线对话</router-link>
      </header>
      <div class="flex-1 overflow-auto p-6">
        <router-view />
      </div>
    </main>
    <GlobalUserWidget />
  </div>
</template>

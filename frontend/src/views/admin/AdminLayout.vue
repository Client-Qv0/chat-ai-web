<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
</script>

<template>
  <div class="flex h-screen">
    <aside class="w-48 bg-gray-50 border-r flex flex-col">
      <div class="p-4">
        <h2 class="text-lg font-bold text-gray-800">后台管理</h2>
      </div>
      <el-menu :default-active="route.path" router class="flex-1 border-r-0">
        <el-menu-item index="/admin/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>系统概览</span>
        </el-menu-item>
        <el-menu-item index="/admin/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/conversations">
          <el-icon><ChatDotRound /></el-icon>
          <span>对话管理</span>
        </el-menu-item>
      </el-menu>
    </aside>
    <main class="flex-1 flex flex-col">
      <header class="h-14 border-b flex items-center justify-between px-4">
        <span class="text-sm text-gray-500">管理员面板</span>
        <router-link to="/chat" class="text-sm text-blue-500 hover:underline">返回前台</router-link>
      </header>
      <div class="flex-1 overflow-auto p-6">
        <router-view />
      </div>
    </main>
  </div>
</template>

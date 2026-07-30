<script setup lang="ts">
import { ElMessage } from 'element-plus'

function goRoot() {
  ElMessage.info('后台管理面板（后续开发）')
}
</script>

<template>
  <div class="flex h-screen">
    <aside class="w-48 bg-gray-50 border-r p-4">
      <p class="text-sm text-gray-500">管理菜单（建设中）</p>
    </aside>
    <main class="flex-1 flex flex-col">
      <header class="h-14 border-b flex items-center justify-between px-4">
        <h1 class="text-lg font-bold">后台管理</h1>
        <el-button type="warning" size="small" @click="goRoot">root</el-button>
      </header>
      <div class="flex-1 flex items-center justify-center text-gray-400">
        <p>管理面板开发中，敬请期待</p>
      </div>
    </main>
  </div>
</template>

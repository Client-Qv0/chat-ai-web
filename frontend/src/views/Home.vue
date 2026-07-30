<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="grid grid-cols-2 gap-8 max-w-4xl">
      <div class="bg-white rounded-2xl shadow-lg p-8 text-center hover:shadow-xl transition-shadow cursor-pointer" @click="$router.push('/chat')">
        <h2 class="text-2xl font-bold mb-2">在线对话</h2>
        <p class="text-gray-500">基于本地大模型的智能对话服务，支持流式输出、多轮对话</p>
        <el-button type="primary" size="large" class="mt-4">进入对话</el-button>
      </div>
      <div class="bg-white rounded-2xl shadow-lg p-8 text-center hover:shadow-xl transition-shadow cursor-pointer" @click="$router.push('/api')">
        <h2 class="text-2xl font-bold mb-2">API 服务</h2>
        <p class="text-gray-500">标准化 API 接口，支持 OpenAI 兼容格式调用</p>
        <el-button type="success" size="large" class="mt-4">进入 API</el-button>
      </div>
    </div>
  </div>
</template>

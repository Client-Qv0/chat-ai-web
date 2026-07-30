<script setup lang="ts">
import { computed } from 'vue'
import MarkdownIt from 'markdown-it'
import type { Message } from '@/types'

const props = defineProps<{ message: Message }>()
const md = new MarkdownIt({ breaks: true })

const renderedHtml = computed(() => md.render(props.message.content))
const isUser = computed(() => props.message.role === 'user')
</script>

<template>
  <div class="flex" :class="isUser ? 'justify-end' : 'justify-start'">
    <div
      class="max-w-[80%] rounded-xl px-4 py-2"
      :class="isUser ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-900'"
    >
      <div v-if="isUser" class="whitespace-pre-wrap">{{ message.content }}</div>
      <div v-else class="prose prose-sm max-w-none" v-html="renderedHtml" />
    </div>
  </div>
</template>

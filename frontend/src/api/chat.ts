import apiClient from './client'
import type { Conversation, Message } from '@/types'

export const chatApi = {
  getConversations: () => apiClient.get<Conversation[]>('/chat/conversations'),
  createConversation: () => apiClient.post<Conversation>('/chat/conversations'),
  getMessages: (routeId: string) => apiClient.get<Message[]>(`/chat/conversations/${routeId}/messages`),
}

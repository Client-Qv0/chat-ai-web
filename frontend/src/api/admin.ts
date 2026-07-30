import apiClient from './client'
import type { AdminStats, AdminUser, AdminConversation, AdminMessage } from '@/types'

export const adminApi = {
  getStats: () => apiClient.get<AdminStats>('/admin/stats'),
  getUsers: () => apiClient.get<AdminUser[]>('/admin/users'),
  updateUserRole: (userId: string, role: string) =>
    apiClient.put<AdminUser>(`/admin/users/${userId}/role`, { role }),
  getConversations: () => apiClient.get<AdminConversation[]>('/admin/conversations'),
  getConversationMessages: (convId: string) =>
    apiClient.get<AdminMessage[]>(`/admin/conversations/${convId}/messages`),
}

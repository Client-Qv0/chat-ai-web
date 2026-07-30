import apiClient from './client'
import type { ApiKey, ApiKeyGenerated } from '@/types'

export const apiKeysApi = {
  list: () => apiClient.get<ApiKey[]>('/api-keys/'),
  generate: () => apiClient.post<ApiKeyGenerated>('/api-keys/generate'),
  revoke: (id: string) => apiClient.delete(`/api-keys/${id}`),
}

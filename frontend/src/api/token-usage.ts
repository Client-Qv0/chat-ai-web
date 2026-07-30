import apiClient from './client'
import type { TokenUsageSummary, DailyUsage } from '@/types'

export const tokenUsageApi = {
  getSummary: () => apiClient.get<TokenUsageSummary>('/token-usage/summary'),
  getDaily: (days = 7) => apiClient.get<DailyUsage[]>('/token-usage/daily', { params: { days } }),
}

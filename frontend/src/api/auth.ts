import apiClient from './client'
import type { LoginRequest, RegisterRequest, LoginResponse, UserInfo } from '@/types'

export const authApi = {
  register: (data: RegisterRequest) => apiClient.post<LoginResponse>('/auth/register', data),
  login: (data: LoginRequest) => apiClient.post<LoginResponse>('/auth/login', data),
  getMe: () => apiClient.get<UserInfo>('/auth/me'),
  updateProfile: (data: { username: string }) => apiClient.put<UserInfo>('/auth/me/profile', data),
  changePassword: (data: { old_password: string; new_password: string }) =>
    apiClient.put('/auth/me/password', data),
}

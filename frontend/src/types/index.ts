export interface UserInfo {
  id: string
  username: string
  phone: string
  role: string
  avatar_url: string
  created_at: string
}

export interface LoginRequest {
  phone: string
  password: string
}

export interface RegisterRequest {
  username: string
  phone: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user_info: UserInfo
}

export interface Conversation {
  id: string
  route_id: string
  title: string
  created_at: string
}

export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  metadata: Record<string, any>
  tokens_used: number
  created_at: string
}

export interface ApiKey {
  id: string
  key_prefix: string
  status: 'active' | 'revoked'
  created_at: string
}

export interface ApiKeyGenerated extends ApiKey {
  full_key: string
}

export interface TokenUsageSummary {
  total_tokens: number
  today_tokens: number
}

export interface DailyUsage {
  date: string
  prompt_tokens: number
  completion_tokens: number
  total_tokens: number
}

export interface AdminStats {
  total_users: number
  total_conversations: number
  total_messages: number
  total_tokens: number
}

export interface AdminUser {
  id: string
  username: string
  phone: string
  role: string
  created_at: string
}

export interface AdminConversation {
  id: string
  route_id: string
  title: string
  username: string
  phone: string
  created_at: string
}

export interface AdminMessage {
  id: string
  role: string
  content: string
  tokens_used: number
  created_at: string
}

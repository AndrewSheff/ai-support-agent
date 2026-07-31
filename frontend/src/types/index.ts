export interface User {
  id: string
  email: string
  name: string
  role: 'admin' | 'user'
  is_active: boolean
  created_at: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User & { must_change_password: boolean }
}

export interface Conversation {
  id: string
  title: string
  created_at: string
  updated_at: string
  message_count: number
  last_message_preview: string | null
}

export interface ConversationDetail {
  id: string
  title: string
  created_at: string
  updated_at: string
  message_count: number
  messages: Message[]
}

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  model: string | null
  sources: Source[] | null
  created_at: string
}

export interface Source {
  document_id: string
  document_name: string
  chunk_index: number
  relevance_score: number
  snippet: string
}

export interface SendMessageResponse {
  user_message: Message
  assistant_message: Message
  conversation_title: string
}

export interface Document {
  id: string
  original_name: string
  file_type: 'pdf' | 'docx' | 'txt'
  file_size: number
  status: 'uploaded' | 'processing' | 'indexed' | 'error'
  page_count: number | null
  chunk_count: number
  uploaded_by: { id: string; name: string }
  error_message: string | null
  created_at: string
  updated_at: string
}

export interface UserWithPassword extends User {
  temporary_password: string
}

export interface StatsResponse {
  total_users: number
  active_users: number
  total_documents: number
  indexed_documents: number
  total_conversations: number
  questions_in_period: number
  questions_change_percent: number | null
}

export interface ActivityItem {
  date: string
  questions: number
}

export interface TopQuestion {
  question: string
  count: number
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  per_page: number
  pages: number
}

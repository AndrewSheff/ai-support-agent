import type { Conversation, ConversationDetail, PaginatedResponse, SendMessageResponse } from '@/types'
import apiClient from './client'

/**
 * Получаем список бесед с поиском и пагинацией
 */
export async function getConversations(params?: {
  search?: string
  page?: number
  per_page?: number
}): Promise<PaginatedResponse<Conversation>> {
  const { data } = await apiClient.get<PaginatedResponse<Conversation>>('/conversations/', {
    params,
  })
  return data
}

/**
 * Создаем новую беседу (можно сразу задать заголовок)
 */
export async function createConversation(title?: string): Promise<ConversationDetail> {
  const { data } = await apiClient.post<ConversationDetail>('/conversations/', { title })
  return data
}

/**
 * Достаем конкретную беседу со всеми сообщениями
 */
export async function getConversation(id: string): Promise<ConversationDetail> {
  const { data } = await apiClient.get<ConversationDetail>(`/conversations/${id}`)
  return data
}

/**
 * Удаляем беседу — прощай, чат
 */
export async function deleteConversation(id: string): Promise<void> {
  await apiClient.delete(`/conversations/${id}`)
}

/**
 * Отправляем сообщение в беседу, указывая модель
 */
export async function sendMessage(
  conversationId: string,
  content: string,
  model: string,
): Promise<SendMessageResponse> {
  const { data } = await apiClient.post<SendMessageResponse>(
    `/conversations/${conversationId}/messages`,
    { content, model },
  )
  return data
}

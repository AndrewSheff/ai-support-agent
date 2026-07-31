import type { Document, PaginatedResponse } from '@/types'
import apiClient from './client'

/**
 * Список документов с фильтрацией по статусу и пагинацией
 */
export async function getDocuments(params?: {
  status?: string
  page?: number
  per_page?: number
}): Promise<PaginatedResponse<Document>> {
  const { data } = await apiClient.get<PaginatedResponse<Document>>('/documents/', { params })
  return data
}

/**
 * Загрузка документа — шлем файл через FormData, multipart
 */
export async function uploadDocument(file: File): Promise<Document> {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await apiClient.post<Document>('/documents/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

/**
 * Удаляем документ по id — без возврата
 */
export async function deleteDocument(id: string): Promise<void> {
  await apiClient.delete(`/documents/${id}`)
}

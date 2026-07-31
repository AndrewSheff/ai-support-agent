import type { PaginatedResponse, User, UserWithPassword } from '@/types'
import apiClient from './client'

/**
 * Список юзеров с пагинацией — для админки
 */
export async function getUsers(params?: {
  page?: number
  per_page?: number
}): Promise<PaginatedResponse<User>> {
  const { data } = await apiClient.get<PaginatedResponse<User>>('/users/', { params })
  return data
}

/**
 * Создаем нового юзера — получаем обратно данные с временным паролем
 */
export async function createUser(userData: {
  email: string
  name: string
  role: string
}): Promise<UserWithPassword> {
  const { data } = await apiClient.post<UserWithPassword>('/users/', userData)
  return data
}

/**
 * Обновляем юзера — можно поменять имя, роль, активность
 */
export async function updateUser(
  id: string,
  userData: Partial<{ name: string; role: string; is_active: boolean }>,
): Promise<User> {
  const { data } = await apiClient.patch<User>(`/users/${id}`, userData)
  return data
}

/**
 * Удаляем юзера — прощай, дружище
 */
export async function deleteUser(id: string): Promise<void> {
  await apiClient.delete(`/users/${id}`)
}

/**
 * Обновление своего профиля — только имя
 */
export async function updateProfile(name: string): Promise<User> {
  const { data } = await apiClient.patch<User>('/users/me/profile', { name })
  return data
}

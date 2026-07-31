import type { LoginResponse } from '@/types'
import apiClient from './client'

/**
 * Логин — отправляем email + пароль, получаем токен и данные юзера
 */
export async function login(email: string, password: string): Promise<LoginResponse> {
  const { data } = await apiClient.post<LoginResponse>('/auth/login', { email, password })
  return data
}

/**
 * Смена пароля — текущий, новый и подтверждение нового
 */
export async function changePassword(
  currentPassword: string,
  newPassword: string,
  confirmPassword: string,
): Promise<void> {
  await apiClient.post('/auth/change-password', {
    current_password: currentPassword,
    new_password: newPassword,
    confirm_password: confirmPassword,
  })
}

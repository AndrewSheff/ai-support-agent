import { useContext } from 'react'
import { AuthContext } from '@/contexts/AuthContext'

/**
 * Хук для доступа к контексту авторизации.
 * Если использовать вне AuthProvider — кинет ошибку, чтоб не гадать потом.
 */
export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within AuthProvider')
  return context
}

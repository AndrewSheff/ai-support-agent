import { createContext, useCallback, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import type { User } from '@/types'
import * as authApi from '@/api/auth'

/** Данные юзера из JWT-токена + флаг смены пароля */
interface AuthUser extends User {
  must_change_password: boolean
}

/** Что предоставляет наш AuthContext потребителям */
export interface AuthContextValue {
  token: string | null
  user: AuthUser | null
  isAuthenticated: boolean
  isAdmin: boolean
  mustChangePassword: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
}

// Создаем контекст — null по умолчанию, пока провайдер не подключен
export const AuthContext = createContext<AuthContextValue | null>(null)

/** Пейлоад из JWT — то, что зашито в средней части токена */
interface JwtPayload {
  exp: number
  sub: string
  email: string
  role: 'admin' | 'user'
}

/**
 * Декодируем JWT — вытаскиваем среднюю часть (payload) через atob.
 * Если токен кривой — вернем null, не будем падать.
 */
function decodeJwt(token: string): JwtPayload | null {
  try {
    const parts = token.split('.')
    if (parts.length !== 3) return null
    const payload = JSON.parse(atob(parts[1]!)) as JwtPayload
    return payload
  } catch {
    return null
  }
}

/**
 * Восстанавливаем юзера из сохраненного токена.
 * Если токен протух — возвращаем null.
 */
function restoreUserFromToken(token: string): AuthUser | null {
  const payload = decodeJwt(token)
  if (!payload) return null

  // Проверяем, не истек ли токен
  const now = Math.floor(Date.now() / 1000)
  if (payload.exp < now) return null

  return {
    id: payload.sub,
    email: payload.email,
    name: '', // имя из JWT не достанешь, оставляем пустым
    role: payload.role,
    is_active: true,
    created_at: '',
    must_change_password: false,
  }
}

/**
 * Провайдер авторизации — оборачиваем приложение, раздаем контекст.
 * При маунте пытаемся восстановить сессию из localStorage.
 */
export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => {
    const savedToken = localStorage.getItem('auth_token')
    if (!savedToken) return null

    // Проверяем валидность токена при инициализации
    const user = restoreUserFromToken(savedToken)
    if (!user) {
      localStorage.removeItem('auth_token')
      return null
    }
    return savedToken
  })

  const [user, setUser] = useState<AuthUser | null>(() => {
    const savedToken = localStorage.getItem('auth_token')
    if (!savedToken) return null
    return restoreUserFromToken(savedToken)
  })

  // На всякий случай — если токен сброшен, юзера тоже чистим
  useEffect(() => {
    if (!token) {
      setUser(null)
    }
  }, [token])

  // Логин — дергаем API, сохраняем токен и данные юзера
  const login = useCallback(async (email: string, password: string) => {
    const response = await authApi.login(email, password)
    localStorage.setItem('auth_token', response.access_token)
    setToken(response.access_token)
    setUser(response.user)
  }, [])

  // Логаут — чистим все и отправляем на /login
  const logout = useCallback(() => {
    localStorage.removeItem('auth_token')
    setToken(null)
    setUser(null)
    window.location.href = '/login'
  }, [])

  // Мемоизируем значение контекста, чтобы не ререндерить все подряд
  const value = useMemo<AuthContextValue>(
    () => ({
      token,
      user,
      isAuthenticated: !!token && !!user,
      isAdmin: user?.role === 'admin',
      mustChangePassword: user?.must_change_password ?? false,
      login,
      logout,
    }),
    [token, user, login, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

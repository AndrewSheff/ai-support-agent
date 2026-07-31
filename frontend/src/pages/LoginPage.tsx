import { useState, type FormEvent, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Bot, Mail, Eye, EyeOff, Loader2, AlertCircle } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Alert, AlertDescription } from '@/components/ui/alert'

/**
 * Страница логина — классика жанра: email + пароль.
 * Если юзер уже залогинен, сразу кидаем на нужную страницу.
 */
export default function LoginPage() {
  const { login, isAuthenticated, isAdmin } = useAuth()
  const navigate = useNavigate()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const emailInputRef = useRef<HTMLInputElement>(null)

  // Автофокус на email при маунте
  useEffect(() => {
    emailInputRef.current?.focus()
  }, [])

  // Уже авторизован — перенаправляем
  useEffect(() => {
    if (isAuthenticated) {
      navigate(isAdmin ? '/dashboard' : '/chat', { replace: true })
    }
  }, [isAuthenticated, isAdmin, navigate])

  // Простенькая валидация email (не сложнее чем нужно)
  const isEmailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
  const isFormValid = isEmailValid && password.length > 0

  /** Отправляем форму логина */
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!isFormValid || isLoading) return

    setError(null)
    setIsLoading(true)

    try {
      const result = await login(email, password)
      // Если юзеру надо сменить пароль, редирект произойдет через ProtectedRoute
      // Иначе кидаем по роли
      if (!result.user.must_change_password) {
        navigate(result.user.role === 'admin' ? '/dashboard' : '/chat', { replace: true })
      }
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Something went wrong. Please try again.'
      setError(message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-[400px]">
        {/* Карточка логина */}
        <div className="rounded-xl border bg-white p-8 shadow-sm">
          {/* Шапка с логотипом */}
          <div className="mb-8 text-center">
            <div className="mb-4 flex justify-center">
              <Bot className="h-10 w-10 text-primary" />
            </div>
            <h1 className="text-2xl font-bold">AI Support Agent</h1>
            <p className="mt-2 text-sm text-muted-foreground">
              Sign in to your account
            </p>
          </div>

          {/* Ошибка авторизации, если есть */}
          {error && (
            <Alert variant="destructive" className="mb-6">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Форма входа */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Email */}
            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium">
                Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  ref={emailInputRef}
                  id="email"
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="pl-10"
                  disabled={isLoading}
                  autoComplete="email"
                />
              </div>
            </div>

            {/* Пароль с toggle видимости */}
            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium">
                Password
              </label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="pr-10"
                  disabled={isLoading}
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  tabIndex={-1}
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </button>
              </div>
            </div>

            {/* Кнопка входа */}
            <Button
              type="submit"
              className="w-full"
              disabled={!isFormValid || isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Signing in...
                </>
              ) : (
                'Sign In'
              )}
            </Button>
          </form>
        </div>

        {/* Футер */}
        <p className="mt-6 text-center text-xs text-slate-400">
          Powered by AI Support Agent
        </p>
      </div>
    </div>
  )
}

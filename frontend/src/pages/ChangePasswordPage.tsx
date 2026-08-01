import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { Shield, Eye, EyeOff, Loader2, Check, X } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'
import { changePassword } from '@/api/auth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { toast } from 'sonner'

/**
 * Страница смены пароля при первом входе.
 * Показываем требования к паролю в реалтайме — пользователь видит что ему надо исправить.
 */
export default function ChangePasswordPage() {
  const { user, isAdmin } = useAuth()
  const navigate = useNavigate()

  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showCurrentPassword, setShowCurrentPassword] = useState(false)
  const [showNewPassword, setShowNewPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  // Если юзер зашел сюда не по делу (пароль менять не надо) — выкидываем
  if (user && !user.must_change_password) {
    navigate(isAdmin ? '/dashboard' : '/chat', { replace: true })
    return null
  }

  // Чеклист требований к паролю
  const requirements = [
    { label: 'At least 8 characters', met: newPassword.length >= 8 },
    { label: 'Contains a letter', met: /[a-zA-Z]/.test(newPassword) },
    { label: 'Contains a number', met: /\d/.test(newPassword) },
    {
      label: 'Passwords match',
      met: confirmPassword.length > 0 && newPassword === confirmPassword,
    },
  ]

  const allRequirementsMet = requirements.every((r) => r.met) && currentPassword.length > 0

  /** Отправляем новый пароль */
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!allRequirementsMet || isLoading) return

    setIsLoading(true)

    try {
      await changePassword(currentPassword, newPassword, confirmPassword)
      toast.success('Password changed successfully')
      // Даем секунду чтобы юзер увидел тост, потом редирект
      setTimeout(() => {
        navigate(isAdmin ? '/dashboard' : '/chat', { replace: true })
      }, 1000)
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Failed to change password'
      toast.error(message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-[400px]">
        <div className="rounded-xl border bg-white p-8 shadow-sm">
          {/* Шапка — щит и заголовок */}
          <div className="mb-8 text-center">
            <div className="mb-4 flex justify-center">
              <Shield className="h-10 w-10 text-amber-500" />
            </div>
            <h1 className="text-2xl font-bold">Change Password</h1>
            <p className="mt-2 text-sm text-muted-foreground">
              Please set a new password for your account
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Текущий пароль (временный, выданный админом) */}
            <div className="space-y-2">
              <label htmlFor="current-password" className="text-sm font-medium">
                Current Password
              </label>
              <div className="relative">
                <Input
                  id="current-password"
                  type={showCurrentPassword ? 'text' : 'password'}
                  placeholder="Enter current password"
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  className="pr-10"
                  disabled={isLoading}
                  autoComplete="current-password"
                  autoFocus
                />
                <button
                  type="button"
                  onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  tabIndex={-1}
                >
                  {showCurrentPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </button>
              </div>
            </div>

            {/* Новый пароль */}
            <div className="space-y-2">
              <label htmlFor="new-password" className="text-sm font-medium">
                New Password
              </label>
              <div className="relative">
                <Input
                  id="new-password"
                  type={showNewPassword ? 'text' : 'password'}
                  placeholder="Enter new password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="pr-10"
                  disabled={isLoading}
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  onClick={() => setShowNewPassword(!showNewPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  tabIndex={-1}
                >
                  {showNewPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </button>
              </div>
            </div>

            {/* Подтверждение пароля */}
            <div className="space-y-2">
              <label htmlFor="confirm-password" className="text-sm font-medium">
                Confirm Password
              </label>
              <div className="relative">
                <Input
                  id="confirm-password"
                  type={showConfirmPassword ? 'text' : 'password'}
                  placeholder="Confirm new password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="pr-10"
                  disabled={isLoading}
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  tabIndex={-1}
                >
                  {showConfirmPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </button>
              </div>
            </div>

            {/* Чеклист требований — зеленые галочки или серые крестики */}
            <div className="space-y-2 rounded-md bg-slate-50 p-3">
              {requirements.map((req) => (
                <div
                  key={req.label}
                  className="flex items-center gap-2 text-sm"
                >
                  {req.met ? (
                    <Check className="h-4 w-4 text-green-500" />
                  ) : (
                    <X className="h-4 w-4 text-slate-300" />
                  )}
                  <span className={req.met ? 'text-green-700' : 'text-slate-500'}>
                    {req.label}
                  </span>
                </div>
              ))}
            </div>

            {/* Кнопка сабмита */}
            <Button
              type="submit"
              className="w-full"
              disabled={!allRequirementsMet || isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Updating...
                </>
              ) : (
                'Update Password'
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

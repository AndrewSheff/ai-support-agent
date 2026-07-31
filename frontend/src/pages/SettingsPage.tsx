import { useState, type FormEvent } from 'react'
import { Eye, EyeOff, Loader2, Check, X } from 'lucide-react'
import { toast } from 'sonner'
import { useAuth } from '@/hooks/useAuth'
import { updateProfile } from '@/api/users'
import { changePassword } from '@/api/auth'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'

/**
 * Страница настроек профиля — редактирование имени и смена пароля.
 * Тут юзер может подправить свои данные, без всяких лишних наворотов.
 */
export default function SettingsPage() {
  return (
    <div className="p-6">
      <div className="max-w-2xl mx-auto space-y-6">
        <h1 className="text-2xl font-bold">Settings</h1>

        {/* Карточка профиля */}
        <ProfileCard />

        {/* Карточка смены пароля */}
        <ChangePasswordCard />
      </div>
    </div>
  )
}

/**
 * Карточка профиля — имя можно менять, email и роль только для чтения.
 * Save кнопка активна только если имя реально поменялось.
 */
function ProfileCard() {
  const { user } = useAuth()

  const [name, setName] = useState(user?.name ?? '')
  const [isLoading, setIsLoading] = useState(false)

  // Имя изменилось — можно сохранять
  const hasChanges = name.trim() !== (user?.name ?? '') && name.trim().length >= 2

  /** Сохраняем новое имя */
  const handleSave = async (e: FormEvent) => {
    e.preventDefault()
    if (!hasChanges || isLoading) return

    setIsLoading(true)
    try {
      await updateProfile(name.trim())
      toast.success('Profile updated')
    } catch {
      toast.error('Failed to update profile')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Profile</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSave} className="space-y-4">
          {/* Имя — редактируемое */}
          <div className="space-y-2">
            <Label htmlFor="profile-name">Name</Label>
            <Input
              id="profile-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              disabled={isLoading}
              placeholder="Your name"
            />
          </div>

          {/* Email — только чтение, серый фон */}
          <div className="space-y-2">
            <Label htmlFor="profile-email">Email</Label>
            <Input
              id="profile-email"
              value={user?.email ?? ''}
              disabled
              className="bg-slate-50"
            />
          </div>

          {/* Роль — просто бейдж */}
          <div className="space-y-2">
            <Label>Role</Label>
            <div>
              <Badge variant="secondary" className="capitalize">
                {user?.role ?? 'user'}
              </Badge>
            </div>
          </div>

          {/* Кнопка сохранения */}
          <Button type="submit" disabled={!hasChanges || isLoading}>
            {isLoading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Saving...
              </>
            ) : (
              'Save Changes'
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}

/**
 * Карточка смены пароля — текущий + новый + подтверждение.
 * Требования к паролю показываются чеклистом, как на ChangePasswordPage.
 */
function ChangePasswordCard() {
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')

  const [showCurrentPassword, setShowCurrentPassword] = useState(false)
  const [showNewPassword, setShowNewPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)

  const [isLoading, setIsLoading] = useState(false)

  // Чеклист требований к паролю — как на странице первой смены
  const requirements = [
    { label: 'At least 8 characters', met: newPassword.length >= 8 },
    { label: 'Contains a letter', met: /[a-zA-Z]/.test(newPassword) },
    { label: 'Contains a number', met: /\d/.test(newPassword) },
    {
      label: 'Passwords match',
      met: confirmPassword.length > 0 && newPassword === confirmPassword,
    },
  ]

  const allRequirementsMet = requirements.every((r) => r.met)
  const isFormValid = currentPassword.length > 0 && allRequirementsMet

  /** Отправляем смену пароля */
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!isFormValid || isLoading) return

    setIsLoading(true)
    try {
      await changePassword(currentPassword, newPassword, confirmPassword)
      toast.success('Password updated successfully')
      // Чистим форму после успеха
      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Failed to update password'
      toast.error(message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Change Password</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Текущий пароль */}
          <div className="space-y-2">
            <Label htmlFor="current-password">Current Password</Label>
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
            <Label htmlFor="new-password">New Password</Label>
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
            <Label htmlFor="confirm-password-settings">Confirm Password</Label>
            <div className="relative">
              <Input
                id="confirm-password-settings"
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

          {/* Чеклист требований к паролю */}
          {newPassword.length > 0 && (
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
                  <span
                    className={req.met ? 'text-green-700' : 'text-slate-500'}
                  >
                    {req.label}
                  </span>
                </div>
              ))}
            </div>
          )}

          {/* Кнопка обновления пароля */}
          <Button type="submit" disabled={!isFormValid || isLoading}>
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
      </CardContent>
    </Card>
  )
}

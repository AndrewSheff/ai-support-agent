import { useState, type FormEvent } from 'react'
import {
  UserPlus,
  Trash2,
  ChevronLeft,
  ChevronRight,
  Loader2,
  Copy,
  Check,
  AlertTriangle,
} from 'lucide-react'
import { toast } from 'sonner'
import {
  useUsers,
  useCreateUser,
  useUpdateUser,
  useDeleteUser,
} from '@/hooks/useUsers'
import { useAuth } from '@/hooks/useAuth'
import { formatRelativeTime, cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import type { User, UserWithPassword } from '@/types'

/**
 * Страница управления пользователями — список, создание, редактирование ролей и статуса.
 * Админ рулит тут юзерами: кого создать, кого деактивировать, кому какую роль дать.
 */
export default function UsersPage() {
  const { user: currentUser } = useAuth()
  const [page, setPage] = useState(1)
  const [addDialogOpen, setAddDialogOpen] = useState(false)
  const [deleteTarget, setDeleteTarget] = useState<User | null>(null)
  const [deactivateTarget, setDeactivateTarget] = useState<User | null>(null)

  const { data, isLoading } = useUsers(page)
  const updateUser = useUpdateUser()
  const deleteUser = useDeleteUser()

  const users = data?.items ?? []
  const totalPages = data?.pages ?? 1

  /** Смена роли юзера — сразу отправляем на сервер */
  const handleRoleChange = async (userId: string, role: string) => {
    try {
      await updateUser.mutateAsync({ id: userId, data: { role } })
      toast.success('Role updated')
    } catch {
      toast.error('Failed to update role')
    }
  }

  /** Переключение активности юзера */
  const handleToggleActive = (user: User) => {
    if (user.is_active) {
      // Деактивация — спрашиваем подтверждение
      setDeactivateTarget(user)
    } else {
      // Активация — сразу
      void performToggleActive(user.id, true)
    }
  }

  /** Непосредственно переключаем активность */
  const performToggleActive = async (userId: string, activate: boolean) => {
    try {
      await updateUser.mutateAsync({
        id: userId,
        data: { is_active: activate },
      })
      toast.success(activate ? 'User activated' : 'User deactivated')
    } catch {
      toast.error('Failed to update user status')
    }
  }

  /** Удаление юзера */
  const handleDelete = async () => {
    if (!deleteTarget) return
    try {
      await deleteUser.mutateAsync(deleteTarget.id)
      toast.success('User deleted')
    } catch {
      toast.error('Failed to delete user')
    } finally {
      setDeleteTarget(null)
    }
  }

  /** Подтверждение деактивации */
  const handleDeactivateConfirm = async () => {
    if (!deactivateTarget) return
    await performToggleActive(deactivateTarget.id, false)
    setDeactivateTarget(null)
  }

  return (
    <div className="p-6 space-y-6">
      {/* Шапка */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Users</h1>
        <Button onClick={() => setAddDialogOpen(true)}>
          <UserPlus className="h-4 w-4" />
          Add User
        </Button>
      </div>

      {/* Таблица юзеров */}
      <div className="rounded-lg border bg-white">
        {/* Заголовки столбцов */}
        <div className="grid grid-cols-[1fr_120px_100px_100px_50px] gap-4 border-b px-4 py-3 text-sm font-medium text-muted-foreground">
          <span>User</span>
          <span>Role</span>
          <span>Status</span>
          <span>Created</span>
          <span />
        </div>

        {/* Строки таблицы */}
        {isLoading ? (
          <div className="p-4 space-y-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-14 w-full" />
            ))}
          </div>
        ) : users.length === 0 ? (
          <div className="py-16 text-center text-muted-foreground">
            No users found
          </div>
        ) : (
          users.map((user) => {
            const isCurrentUser = user.id === currentUser?.id

            return (
              <div
                key={user.id}
                className={cn(
                  'grid grid-cols-[1fr_120px_100px_100px_50px] gap-4 items-center border-b last:border-b-0 px-4 py-3 text-sm transition-colors',
                  isCurrentUser ? 'bg-primary/5' : 'hover:bg-slate-50',
                )}
              >
                {/* Юзер: аватарка + имя + email */}
                <div className="flex items-center gap-3 min-w-0">
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary text-sm font-medium text-white">
                    {user.name.charAt(0).toUpperCase()}
                  </div>
                  <div className="min-w-0">
                    <p className="truncate font-medium">
                      {user.name}
                      {isCurrentUser && (
                        <span className="ml-1 text-xs text-muted-foreground">
                          (you)
                        </span>
                      )}
                    </p>
                    <p className="truncate text-xs text-muted-foreground">
                      {user.email}
                    </p>
                  </div>
                </div>

                {/* Роль — inline select */}
                <div>
                  <Select
                    value={user.role}
                    onValueChange={(value) =>
                      handleRoleChange(user.id, value)
                    }
                    disabled={isCurrentUser}
                  >
                    <SelectTrigger className="h-8 w-[110px]">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="admin">Admin</SelectItem>
                      <SelectItem value="user">User</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Статус — toggle switch */}
                <div className="flex items-center gap-2">
                  <Switch
                    checked={user.is_active}
                    onCheckedChange={() => handleToggleActive(user)}
                    disabled={isCurrentUser}
                  />
                  <span
                    className={cn(
                      'text-xs',
                      user.is_active
                        ? 'text-green-600'
                        : 'text-slate-400',
                    )}
                  >
                    {user.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>

                {/* Дата создания */}
                <span className="text-muted-foreground">
                  {formatRelativeTime(user.created_at)}
                </span>

                {/* Кнопка удаления */}
                <div>
                  {!isCurrentUser && (
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => setDeleteTarget(user)}
                      className="text-muted-foreground hover:text-destructive"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </div>
            )
          })
        )}
      </div>

      {/* Пагинация */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page <= 1}
          >
            <ChevronLeft className="h-4 w-4" />
            Previous
          </Button>
          <span className="px-3 text-sm text-muted-foreground">
            Page {page} of {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page >= totalPages}
          >
            Next
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      )}

      {/* Диалог добавления юзера */}
      <AddUserDialog
        open={addDialogOpen}
        onOpenChange={setAddDialogOpen}
      />

      {/* Подтверждение удаления */}
      <AlertDialog
        open={!!deleteTarget}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete User</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete &quot;{deleteTarget?.name}&quot;?
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {deleteUser.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Deleting...
                </>
              ) : (
                'Delete'
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Подтверждение деактивации */}
      <AlertDialog
        open={!!deactivateTarget}
        onOpenChange={(open) => !open && setDeactivateTarget(null)}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Deactivate User</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to deactivate &quot;{deactivateTarget?.name}&quot;?
              They will not be able to log in until reactivated.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDeactivateConfirm}>
              Deactivate
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}

/** Пропсы диалога добавления юзера */
interface AddUserDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

/**
 * Диалог добавления нового юзера.
 * После создания показываем credentials — email и временный пароль.
 * Пароль показывается ОДИН раз, поэтому предупреждаем об этом.
 */
function AddUserDialog({ open, onOpenChange }: AddUserDialogProps) {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [role, setRole] = useState('user')
  const [createdUser, setCreatedUser] = useState<UserWithPassword | null>(null)
  const [copied, setCopied] = useState(false)

  const createUser = useCreateUser()

  // Простая валидация формы
  const isNameValid = name.trim().length >= 2
  const isEmailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
  const isFormValid = isNameValid && isEmailValid

  /** Создаем юзера */
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!isFormValid || createUser.isPending) return

    try {
      const result = await createUser.mutateAsync({
        name: name.trim(),
        email: email.trim(),
        role,
      })
      // Не закрываем диалог — показываем credentials
      setCreatedUser(result)
      toast.success('User created successfully')
    } catch {
      toast.error('Failed to create user')
    }
  }

  /** Копируем пароль в буфер обмена */
  const handleCopyPassword = async () => {
    if (!createdUser) return
    try {
      await navigator.clipboard.writeText(createdUser.temporary_password)
      setCopied(true)
      toast.success('Password copied to clipboard')
      setTimeout(() => setCopied(false), 2000)
    } catch {
      toast.error('Failed to copy password')
    }
  }

  /** Закрытие диалога — сбрасываем все состояние */
  const handleClose = () => {
    setName('')
    setEmail('')
    setRole('user')
    setCreatedUser(null)
    setCopied(false)
    onOpenChange(false)
  }

  return (
    <Dialog
      open={open}
      onOpenChange={(v) => {
        if (!v) handleClose()
      }}
    >
      <DialogContent className="sm:max-w-[480px]">
        <DialogHeader>
          <DialogTitle>
            {createdUser ? 'User Created' : 'Add User'}
          </DialogTitle>
          <DialogDescription>
            {createdUser
              ? 'The user has been created. Save the credentials below.'
              : 'Create a new user account. A temporary password will be generated.'}
          </DialogDescription>
        </DialogHeader>

        {createdUser ? (
          /* Показываем credentials после создания */
          <div className="space-y-4">
            <div className="rounded-lg border bg-green-50 p-4 space-y-3">
              <div>
                <p className="text-xs font-medium text-muted-foreground">
                  Email
                </p>
                <p className="text-sm font-medium">{createdUser.email}</p>
              </div>
              <div>
                <p className="text-xs font-medium text-muted-foreground">
                  Temporary Password
                </p>
                <div className="flex items-center gap-2 mt-1">
                  <code className="flex-1 rounded bg-white px-3 py-2 text-sm font-mono border">
                    {createdUser.temporary_password}
                  </code>
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={handleCopyPassword}
                  >
                    {copied ? (
                      <Check className="h-4 w-4 text-green-600" />
                    ) : (
                      <Copy className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>
            </div>

            {/* Предупреждение — пароль показывается один раз */}
            <div className="flex gap-2 rounded-md bg-amber-50 border border-amber-200 p-3">
              <AlertTriangle className="h-4 w-4 shrink-0 text-amber-600 mt-0.5" />
              <p className="text-xs text-amber-700">
                This password will only be shown once. Make sure to save it.
              </p>
            </div>

            <DialogFooter>
              <Button onClick={handleClose} className="w-full sm:w-auto">
                Done
              </Button>
            </DialogFooter>
          </div>
        ) : (
          /* Форма создания юзера */
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="user-name">Name</Label>
              <Input
                id="user-name"
                placeholder="John Doe"
                value={name}
                onChange={(e) => setName(e.target.value)}
                disabled={createUser.isPending}
                autoFocus
              />
              {name.length > 0 && !isNameValid && (
                <p className="text-xs text-destructive">
                  Name must be at least 2 characters
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="user-email">Email</Label>
              <Input
                id="user-email"
                type="email"
                placeholder="john@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={createUser.isPending}
              />
              {email.length > 0 && !isEmailValid && (
                <p className="text-xs text-destructive">
                  Please enter a valid email address
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label>Role</Label>
              <Select
                value={role}
                onValueChange={setRole}
                disabled={createUser.isPending}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="user">User</SelectItem>
                  <SelectItem value="admin">Admin</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <DialogFooter>
              <Button
                type="submit"
                disabled={!isFormValid || createUser.isPending}
                className="w-full sm:w-auto"
              >
                {createUser.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Creating...
                  </>
                ) : (
                  'Create User'
                )}
              </Button>
            </DialogFooter>
          </form>
        )}
      </DialogContent>
    </Dialog>
  )
}

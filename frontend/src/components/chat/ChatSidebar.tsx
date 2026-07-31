import { useCallback, useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Bot,
  Plus,
  Search,
  X,
  Trash2,
  LogOut,
} from 'lucide-react'
import { isToday, isYesterday, subDays, isAfter } from 'date-fns'
import { toast } from 'sonner'
import { useAuth } from '@/hooks/useAuth'
import { useConversations, useCreateConversation, useDeleteConversation } from '@/hooks/useConversations'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
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
import { cn } from '@/lib/utils'
import { SEARCH_DEBOUNCE_MS } from '@/lib/constants'
import type { Conversation } from '@/types'

/** Пропсы сайдбара */
interface ChatSidebarProps {
  currentConversationId?: string
  /** Закрыть сайдбар — нужно для мобилки */
  onClose?: () => void
}

/** Группа бесед с заголовком */
interface ConversationGroup {
  label: string
  conversations: Conversation[]
}

/**
 * Раскидываем беседы по группам: Today, Yesterday, Previous 7 Days и т.д.
 * Сортировка уже предполагается от сервера, тут только группируем.
 */
function groupConversations(conversations: Conversation[]): ConversationGroup[] {
  const now = new Date()
  const sevenDaysAgo = subDays(now, 7)
  const thirtyDaysAgo = subDays(now, 30)

  const groups: Record<string, Conversation[]> = {
    Today: [],
    Yesterday: [],
    'Previous 7 Days': [],
    'Previous 30 Days': [],
    Older: [],
  }

  for (const convo of conversations) {
    const date = new Date(convo.updated_at)
    if (isToday(date)) {
      groups['Today']!.push(convo)
    } else if (isYesterday(date)) {
      groups['Yesterday']!.push(convo)
    } else if (isAfter(date, sevenDaysAgo)) {
      groups['Previous 7 Days']!.push(convo)
    } else if (isAfter(date, thirtyDaysAgo)) {
      groups['Previous 30 Days']!.push(convo)
    } else {
      groups['Older']!.push(convo)
    }
  }

  // Возвращаем только непустые группы
  return Object.entries(groups)
    .filter(([, items]) => items.length > 0)
    .map(([label, conversations]) => ({ label, conversations }))
}

/**
 * Левый сайдбар чата — список бесед с поиском, кнопка "New Chat",
 * инфо о юзере внизу. Темная тема, bg-slate-900.
 */
export function ChatSidebar({ currentConversationId, onClose }: ChatSidebarProps) {
  const navigate = useNavigate()
  const { user, logout } = useAuth()

  // Поиск с debounce — пока юзер печатает, не спамим запросами
  const [searchInput, setSearchInput] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')
  const [deleteTarget, setDeleteTarget] = useState<Conversation | null>(null)

  // Debounce поиска через setTimeout
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchInput)
    }, SEARCH_DEBOUNCE_MS)
    return () => clearTimeout(timer)
  }, [searchInput])

  // Данные и мутации
  const { data: conversationsData, isLoading } = useConversations(
    debouncedSearch || undefined,
  )
  const createConversation = useCreateConversation()
  const deleteConversation = useDeleteConversation()

  const conversations = useMemo(() => conversationsData?.items ?? [], [conversationsData])
  const groups = useMemo(() => groupConversations(conversations), [conversations])

  // Первая буква имени для аватарки
  const userInitial = user?.name?.charAt(0)?.toUpperCase() ?? '?'

  // Создание нового чата
  const handleNewChat = useCallback(async () => {
    try {
      const convo = await createConversation.mutateAsync()
      navigate(`/chat/${convo.id}`)
      onClose?.()
    } catch {
      toast.error('Failed to create conversation')
    }
  }, [createConversation, navigate, onClose])

  // Переход в беседу
  const handleSelectConversation = useCallback(
    (id: string) => {
      navigate(`/chat/${id}`)
      onClose?.()
    },
    [navigate, onClose],
  )

  // Удаление беседы с подтверждением
  const handleConfirmDelete = useCallback(async () => {
    if (!deleteTarget) return
    try {
      await deleteConversation.mutateAsync(deleteTarget.id)
      // Если удалили текущую беседу — уходим на главный чат
      if (deleteTarget.id === currentConversationId) {
        navigate('/chat')
      }
      toast.success('Conversation deleted')
    } catch {
      toast.error('Failed to delete conversation')
    } finally {
      setDeleteTarget(null)
    }
  }, [deleteTarget, deleteConversation, currentConversationId, navigate])

  // Очистка поиска
  const handleClearSearch = useCallback(() => {
    setSearchInput('')
  }, [])

  // Выход из аккаунта
  const handleLogout = useCallback(() => {
    logout()
    navigate('/login')
  }, [logout, navigate])

  return (
    <div className="flex h-full w-[280px] flex-col bg-slate-900 text-slate-100">
      {/* Шапка — логотип и кнопка нового чата */}
      <div className="border-b border-slate-800 p-4">
        <div className="mb-4 flex items-center gap-2">
          <Bot className="h-6 w-6 text-primary-foreground" />
          <span className="text-lg font-bold">AI Support Agent</span>
        </div>
        <Button
          variant="outline"
          className="w-full border-slate-700 bg-transparent text-slate-100 hover:bg-slate-800 hover:text-slate-100"
          onClick={handleNewChat}
          disabled={createConversation.isPending}
        >
          <Plus className="h-4 w-4" />
          New Chat
        </Button>
      </div>

      {/* Поле поиска */}
      <div className="px-3 py-2">
        <div className="relative">
          <Search className="pointer-events-none absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Search conversations..."
            className="w-full rounded-md bg-slate-800 py-1.5 pl-8 pr-8 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-1 focus:ring-slate-600"
          />
          {searchInput && (
            <button
              onClick={handleClearSearch}
              className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>

      {/* Список бесед — скроллируемая область */}
      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          // Скелетоны загрузки
          <div className="space-y-2 px-3 py-2">
            {Array.from({ length: 5 }).map((_, i) => (
              <div
                key={i}
                className="h-10 animate-pulse rounded-md bg-slate-800"
              />
            ))}
          </div>
        ) : conversations.length === 0 ? (
          // Пустой список — ничего не нашли
          <div className="px-3 py-8 text-center text-sm text-slate-500">
            {searchInput ? 'No conversations found' : 'No conversations yet'}
          </div>
        ) : (
          // Группированный список бесед
          groups.map((group) => (
            <div key={group.label}>
              {/* Заголовок группы */}
              <div className="px-3 py-2 text-xs font-medium uppercase text-slate-500">
                {group.label}
              </div>
              {/* Элементы группы */}
              {group.conversations.map((convo) => (
                <div
                  key={convo.id}
                  onClick={() => handleSelectConversation(convo.id)}
                  className={cn(
                    'group flex cursor-pointer items-center gap-2 px-3 py-2 transition-colors hover:bg-slate-800',
                    convo.id === currentConversationId &&
                      'border-l-2 border-primary bg-slate-800/50',
                  )}
                >
                  <span className="min-w-0 flex-1 truncate text-sm">
                    {convo.title || 'New Conversation'}
                  </span>
                  {/* Кнопка удаления — видна только при ховере */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      setDeleteTarget(convo)
                    }}
                    className="shrink-0 opacity-0 transition-opacity group-hover:opacity-100"
                    title="Delete conversation"
                  >
                    <Trash2 className="h-4 w-4 text-red-400 hover:text-red-300" />
                  </button>
                </div>
              ))}
            </div>
          ))
        )}
      </div>

      {/* Блок юзера внизу */}
      <div className="border-t border-slate-800 p-3">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-sm font-medium text-primary-foreground">
            {userInitial}
          </div>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium">{user?.name || 'User'}</p>
            <Badge
              variant="secondary"
              className="mt-0.5 bg-slate-800 text-slate-400 hover:bg-slate-800"
            >
              {user?.role ?? 'user'}
            </Badge>
          </div>
          <button
            onClick={handleLogout}
            className="shrink-0 text-slate-500 transition-colors hover:text-slate-300"
            title="Sign out"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Диалог подтверждения удаления */}
      <AlertDialog
        open={!!deleteTarget}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete conversation?</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete &quot;{deleteTarget?.title || 'this conversation'}&quot;
              and all its messages. This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleConfirmDelete}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}

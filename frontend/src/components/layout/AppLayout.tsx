import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import {
  Bot,
  MessageSquare,
  BarChart3,
  FileText,
  Users,
  Settings,
  LogOut,
} from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'

/** Элемент навигации в сайдбаре */
interface NavItem {
  label: string
  icon: React.ReactNode
  to: string
  /** Если true — показываем только админам */
  adminOnly?: boolean
}

/** Список ссылок в боковом меню */
const navItems: NavItem[] = [
  { label: 'Chat', icon: <MessageSquare className="h-5 w-5" />, to: '/chat' },
  { label: 'Dashboard', icon: <BarChart3 className="h-5 w-5" />, to: '/dashboard', adminOnly: true },
  { label: 'Documents', icon: <FileText className="h-5 w-5" />, to: '/documents', adminOnly: true },
  { label: 'Users', icon: <Users className="h-5 w-5" />, to: '/users', adminOnly: true },
  { label: 'Settings', icon: <Settings className="h-5 w-5" />, to: '/settings' },
]

/**
 * Общий layout для админских страниц — сайдбар слева, контент справа.
 * Чат использует свой отдельный layout, тут только admin-панель и настройки.
 */
export function AppLayout() {
  const { user, isAdmin, logout } = useAuth()
  const navigate = useNavigate()

  /** Выход из аккаунта — разлогиниваемся и топаем на логин */
  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  // Первая буква имени для аватарки
  const userInitial = user?.name?.charAt(0)?.toUpperCase() ?? '?'

  // Фильтруем пункты меню по роли
  const visibleNavItems = navItems.filter(
    (item) => !item.adminOnly || isAdmin,
  )

  return (
    <div className="flex h-screen">
      {/* Сайдбар — фиксированная ширина, не скроллится */}
      <aside className="flex w-[280px] flex-col border-r bg-white">
        {/* Логотип наверху */}
        <div className="flex items-center gap-3 border-b px-6 py-5">
          <Bot className="h-8 w-8 text-primary" />
          <span className="text-lg font-bold">AI Support Agent</span>
        </div>

        {/* Навигация — растягивается на всю свободную высоту */}
        <nav className="flex-1 space-y-1 px-3 py-4">
          {visibleNavItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary/10 text-primary'
                    : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900',
                )
              }
            >
              {item.icon}
              {item.label}
            </NavLink>
          ))}
        </nav>

        {/* Блок юзера внизу — аватарка, имя и кнопка выхода */}
        <div className="border-t px-4 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary text-sm font-medium text-white">
              {userInitial}
            </div>
            <div className="flex-1 overflow-hidden">
              <p className="truncate text-sm font-medium">{user?.name}</p>
              <p className="truncate text-xs text-muted-foreground">{user?.email}</p>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={handleLogout}
              title="Sign out"
              className="shrink-0"
            >
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </aside>

      {/* Основной контент */}
      <main className="flex-1 overflow-auto bg-slate-50">
        <Outlet />
      </main>
    </div>
  )
}

import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'

interface ProtectedRouteProps {
  children: React.ReactNode
  /** Если задана роль — пускаем только её, остальных кидаем на дефолтную страницу */
  requiredRole?: 'admin'
}

/**
 * Обертка для защищенных маршрутов — проверяет авторизацию, смену пароля и роль.
 * Если что-то не так, перенаправляет куда надо.
 */
export function ProtectedRoute({ children, requiredRole }: ProtectedRouteProps) {
  const { isAuthenticated, user } = useAuth()
  const location = useLocation()

  // Не залогинен — на страницу входа
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  // Нужно сменить пароль — принудительно кидаем на смену (кроме самой страницы)
  if (user?.must_change_password && location.pathname !== '/change-password') {
    return <Navigate to="/change-password" replace />
  }

  // Нужна роль admin, а юзер простой — отправляем в чат
  if (requiredRole === 'admin' && user?.role !== 'admin') {
    return <Navigate to="/chat" replace />
  }

  return <>{children}</>
}

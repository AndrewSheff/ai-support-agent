import { lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'sonner'
import { AuthProvider } from '@/contexts/AuthContext'
import { ProtectedRoute } from '@/components/layout/ProtectedRoute'
import { AppLayout } from '@/components/layout/AppLayout'
import { Loader2 } from 'lucide-react'

// Ленивая загрузка страниц — грузим только когда переходим
const LoginPage = lazy(() => import('@/pages/LoginPage'))
const ChangePasswordPage = lazy(() => import('@/pages/ChangePasswordPage'))
const ChatPage = lazy(() => import('@/pages/ChatPage'))
const DashboardPage = lazy(() => import('@/pages/DashboardPage'))
const DocumentsPage = lazy(() => import('@/pages/DocumentsPage'))
const UsersPage = lazy(() => import('@/pages/UsersPage'))
const SettingsPage = lazy(() => import('@/pages/SettingsPage'))
const NotFoundPage = lazy(() => import('@/pages/NotFoundPage'))

/** Настройки react-query — один retry, без рефетча на фокус */
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

/** Спиннер пока lazy-компоненты грузятся */
function PageLoader() {
  return (
    <div className="flex h-screen items-center justify-center">
      <Loader2 className="h-8 w-8 animate-spin text-primary" />
    </div>
  )
}

/**
 * Корневой компонент приложения — все провайдеры и роутинг живут тут.
 */
export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <Suspense fallback={<PageLoader />}>
            <Routes>
              {/* Корень — просто редирект в чат */}
              <Route path="/" element={<Navigate to="/chat" replace />} />

              {/* Публичные страницы */}
              <Route path="/login" element={<LoginPage />} />

              {/* Смена пароля — нужна авторизация, но без проверки роли */}
              <Route
                path="/change-password"
                element={
                  <ProtectedRoute>
                    <ChangePasswordPage />
                  </ProtectedRoute>
                }
              />

              {/* Чат — отдельно, без AppLayout (у него будет свой) */}
              <Route
                path="/chat"
                element={
                  <ProtectedRoute>
                    <ChatPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/chat/:id"
                element={
                  <ProtectedRoute>
                    <ChatPage />
                  </ProtectedRoute>
                }
              />

              {/* Админские страницы внутри AppLayout */}
              <Route
                element={
                  <ProtectedRoute>
                    <AppLayout />
                  </ProtectedRoute>
                }
              >
                <Route
                  path="/dashboard"
                  element={
                    <ProtectedRoute requiredRole="admin">
                      <DashboardPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/documents"
                  element={
                    <ProtectedRoute requiredRole="admin">
                      <DocumentsPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/users"
                  element={
                    <ProtectedRoute requiredRole="admin">
                      <UsersPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/settings"
                  element={
                    <ProtectedRoute>
                      <SettingsPage />
                    </ProtectedRoute>
                  }
                />
              </Route>

              {/* 404 — все остальное */}
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </Suspense>
          <Toaster position="top-right" richColors />
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

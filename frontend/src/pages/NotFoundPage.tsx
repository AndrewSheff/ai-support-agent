import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'

/**
 * Страница 404 — тут делать нечего, кидаем юзера обратно в чат.
 */
export default function NotFoundPage() {
  const navigate = useNavigate()

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-slate-50 px-4">
      <h1 className="text-6xl font-bold text-slate-200">404</h1>
      <h2 className="mt-4 text-xl font-semibold">Page Not Found</h2>
      <p className="mt-2 text-sm text-muted-foreground">
        The page you&apos;re looking for doesn&apos;t exist
      </p>
      <Button className="mt-6" onClick={() => navigate('/chat')}>
        Go to Chat
      </Button>
    </div>
  )
}

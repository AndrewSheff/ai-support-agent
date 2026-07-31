import { useCallback, useEffect, useRef, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { Menu, X, MessageSquare } from 'lucide-react'
import { toast } from 'sonner'
import { useAuth } from '@/hooks/useAuth'
import { useConversation, useSendMessage } from '@/hooks/useMessages'
import { useCreateConversation } from '@/hooks/useConversations'
import { ChatSidebar } from '@/components/chat/ChatSidebar'
import { ChatMessage } from '@/components/chat/ChatMessage'
import { ChatInput } from '@/components/chat/ChatInput'
import { TypingIndicator } from '@/components/chat/TypingIndicator'
import { WelcomeScreen } from '@/components/chat/WelcomeScreen'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import type { Message } from '@/types'

/**
 * Главная страница чата — два основных состояния:
 * 1. /chat — WelcomeScreen, пока юзер не выбрал или не создал беседу
 * 2. /chat/:id — активная беседа со списком сообщений
 *
 * На мобилке сайдбар прячется, открывается через гамбургер.
 */
export default function ChatPage() {
  const { id: conversationId } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { user } = useAuth()

  // Мобильный сайдбар — тогглим видимость
  const [sidebarOpen, setSidebarOpen] = useState(false)
  // Оптимистичное сообщение юзера — показываем сразу, пока AI думает
  const [optimisticMessage, setOptimisticMessage] = useState<Message | null>(null)

  // Скролл к последнему сообщению
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const messagesContainerRef = useRef<HTMLDivElement>(null)

  // Данные текущей беседы
  const {
    data: conversation,
    isLoading: isConversationLoading,
  } = useConversation(conversationId ?? '')

  const sendMessage = useSendMessage()
  const createConversation = useCreateConversation()

  // Авто-скролл вниз при новых сообщениях
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  // Скроллим, когда приходят новые сообщения или появляется оптимистичное
  useEffect(() => {
    scrollToBottom()
  }, [conversation?.messages, optimisticMessage, scrollToBottom])

  // Очищаем оптимистичное сообщение, когда данные обновились
  useEffect(() => {
    if (!sendMessage.isPending) {
      setOptimisticMessage(null)
    }
  }, [sendMessage.isPending])

  // Закрываем мобильный сайдбар при смене беседы
  useEffect(() => {
    setSidebarOpen(false)
  }, [conversationId])

  // Отправка сообщения в существующую беседу
  const handleSendMessage = useCallback(
    async (content: string, model: string) => {
      if (!conversationId) return

      // Оптимистичное сообщение — сразу показываем юзеру
      const tempMessage: Message = {
        id: `temp-${Date.now()}`,
        role: 'user',
        content,
        model: null,
        sources: null,
        created_at: new Date().toISOString(),
      }
      setOptimisticMessage(tempMessage)

      try {
        await sendMessage.mutateAsync({
          conversationId,
          content,
          model,
        })
      } catch {
        toast.error('Failed to send message')
        setOptimisticMessage(null)
      }
    },
    [conversationId, sendMessage],
  )

  // Быстрое действие с WelcomeScreen — создаем беседу и шлем сообщение
  const handleQuickAction = useCallback(
    async (text: string) => {
      try {
        const convo = await createConversation.mutateAsync()
        navigate(`/chat/${convo.id}`)

        // Немного ждем, чтоб навигация отработала, потом шлем сообщение
        const defaultModel = localStorage.getItem('preferred_model') ?? 'claude'
        await sendMessage.mutateAsync({
          conversationId: convo.id,
          content: text,
          model: defaultModel,
        })
      } catch {
        toast.error('Failed to start conversation')
      }
    },
    [createConversation, navigate, sendMessage],
  )

  // Сообщения для рендера — основные + оптимистичное
  const messages = conversation?.messages ?? []
  const allMessages = optimisticMessage
    ? [...messages, optimisticMessage]
    : messages

  const isSending = sendMessage.isPending

  return (
    <div className="flex h-screen overflow-hidden">
      {/* === Сайдбар === */}
      {/* Десктоп — всегда видим */}
      <div className="hidden shrink-0 md:block">
        <ChatSidebar currentConversationId={conversationId} />
      </div>

      {/* Мобилка — оверлей + slide-in */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 md:hidden">
          {/* Затемненный фон */}
          <div
            className="absolute inset-0 bg-black/50"
            onClick={() => setSidebarOpen(false)}
          />
          {/* Сайдбар поверх */}
          <div className="relative z-50 h-full animate-in slide-in-from-left duration-200">
            <ChatSidebar
              currentConversationId={conversationId}
              onClose={() => setSidebarOpen(false)}
            />
          </div>
        </div>
      )}

      {/* === Основной контент === */}
      <div className="flex min-w-0 flex-1 flex-col bg-white">
        {/* Мобильный хедер с гамбургером */}
        <div className="flex items-center gap-3 border-b px-4 py-3 md:hidden">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            {sidebarOpen ? (
              <X className="h-5 w-5" />
            ) : (
              <Menu className="h-5 w-5" />
            )}
          </Button>
          <span className="text-sm font-medium">
            {conversation?.title ?? 'AI Support Agent'}
          </span>
        </div>

        {/* Контент — WelcomeScreen или активная беседа */}
        {!conversationId ? (
          // Нет выбранной беседы — экран приветствия
          <WelcomeScreen onQuickAction={handleQuickAction} />
        ) : isConversationLoading ? (
          // Загрузка беседы — скелетоны
          <div className="flex-1 space-y-4 p-6">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="flex items-start gap-3">
                <Skeleton className="h-8 w-8 rounded-full" />
                <div className="flex-1 space-y-2">
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-16 w-full" />
                </div>
              </div>
            ))}
          </div>
        ) : (
          // Активная беседа — сообщения + инпут
          <>
            {/* Область сообщений — скроллируемая */}
            <div
              ref={messagesContainerRef}
              className="flex-1 overflow-y-auto"
            >
              <div className="mx-auto max-w-3xl p-6">
                {allMessages.length === 0 ? (
                  // Пустая беседа — подсказка
                  <div className="flex h-full flex-col items-center justify-center py-20 text-center">
                    <MessageSquare className="mb-3 h-10 w-10 text-slate-300" />
                    <p className="text-sm text-slate-500">
                      Start a conversation by sending a message below
                    </p>
                  </div>
                ) : (
                  // Список сообщений
                  <div className="space-y-1">
                    {allMessages.map((msg) => (
                      <ChatMessage
                        key={msg.id}
                        message={msg}
                        userName={user?.name}
                      />
                    ))}
                  </div>
                )}

                {/* Индикатор набора — пока AI думает */}
                {isSending && <TypingIndicator />}

                {/* Якорь для авто-скролла */}
                <div ref={messagesEndRef} />
              </div>
            </div>

            {/* Инпут внизу */}
            <ChatInput
              onSend={handleSendMessage}
              isSending={isSending}
            />
          </>
        )}
      </div>
    </div>
  )
}

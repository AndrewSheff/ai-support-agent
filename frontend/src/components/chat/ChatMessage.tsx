import { Bot, FileText } from 'lucide-react'
import Markdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { formatTime } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import type { Message } from '@/types'

/** Пропсы для одного сообщения чата */
interface ChatMessageProps {
  message: Message
  /** Имя юзера — подставляем первую букву в аватарку */
  userName?: string
}

/**
 * Компонент одного сообщения — рисует по-разному для юзера и AI.
 * У AI есть ещё бейдж модели и блок источников, если они пришли.
 */
export function ChatMessage({ message, userName }: ChatMessageProps) {
  const isUser = message.role === 'user'
  const userInitial = userName?.charAt(0)?.toUpperCase() ?? 'U'
  const hasSources = message.sources && message.sources.length > 0

  // Определяем цвет бейджа модели — Claude зеленый, GPT синий
  const modelBadgeClass = message.model?.toLowerCase().includes('claude')
    ? 'bg-emerald-100 text-emerald-700 border-emerald-200'
    : message.model?.toLowerCase().includes('gpt')
      ? 'bg-blue-100 text-blue-700 border-blue-200'
      : 'bg-slate-100 text-slate-700 border-slate-200'

  return (
    <div className="flex items-start gap-3 px-4 py-3">
      {/* Аватарка — буква юзера или иконка бота */}
      {isUser ? (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-slate-200 text-sm font-medium text-slate-600">
          {userInitial}
        </div>
      ) : (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-white">
          <Bot className="h-4 w-4" />
        </div>
      )}

      {/* Тело сообщения */}
      <div className="min-w-0 flex-1">
        {/* Шапка: имя + бейдж модели (у AI) + время */}
        <div className="mb-1 flex items-center gap-2">
          <span className="text-sm font-medium text-slate-900">
            {isUser ? 'You' : 'AI Assistant'}
          </span>
          {!isUser && message.model && (
            <Badge variant="outline" className={modelBadgeClass}>
              {message.model}
            </Badge>
          )}
          <span className="text-xs text-slate-400">
            {formatTime(message.created_at)}
          </span>
        </div>

        {/* Контент — у юзера просто текст, у AI рендерим Markdown */}
        {isUser ? (
          <p className="whitespace-pre-wrap text-sm text-slate-700">
            {message.content}
          </p>
        ) : (
          <div className="prose prose-sm prose-slate max-w-none text-slate-700">
            <Markdown remarkPlugins={[remarkGfm]}>
              {message.content}
            </Markdown>
          </div>
        )}

        {/* Блок источников — только у AI и только если есть */}
        {!isUser && hasSources && (
          <div className="mt-3 rounded-md border border-slate-200 bg-slate-50 p-3">
            <div className="mb-2 flex items-center gap-1.5 text-xs font-medium text-slate-500">
              <FileText className="h-3.5 w-3.5" />
              Sources
            </div>
            <div className="flex flex-wrap gap-1.5">
              {message.sources!.map((source, index) => (
                <span
                  key={`${source.document_id}-${index}`}
                  className="inline-flex max-w-[200px] truncate rounded-full bg-slate-100 px-2.5 py-1 text-xs text-slate-700"
                  title={`Relevance: ${(source.relevance_score * 100).toFixed(0)}%`}
                >
                  {source.document_name}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

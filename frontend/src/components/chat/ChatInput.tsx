import { useCallback, useRef, useState } from 'react'
import { Send } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { ModelSelector } from '@/components/chat/ModelSelector'
import { MAX_MESSAGE_LENGTH } from '@/lib/constants'
import type { ModelKey } from '@/lib/constants'

/** Пропсы для инпута чата */
interface ChatInputProps {
  onSend: (content: string, model: string) => void
  isSending: boolean
}

/**
 * Нижняя панель ввода — селектор модели, textarea с авто-ресайзом и кнопка отправки.
 * Enter отправляет, Shift+Enter — новая строка. Все по классике.
 */
export function ChatInput({ onSend, isSending }: ChatInputProps) {
  const [content, setContent] = useState('')
  const [model, setModel] = useState<ModelKey>(() => {
    const saved = localStorage.getItem('preferred_model')
    return saved === 'claude' || saved === 'gpt' ? saved : 'claude'
  })
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Авто-ресайз textarea — подстраиваем высоту под контент
  const adjustTextareaHeight = useCallback(() => {
    const textarea = textareaRef.current
    if (!textarea) return
    textarea.style.height = 'auto'
    textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`
  }, [])

  // Отправка сообщения — чистим поле, сбрасываем высоту
  const handleSend = useCallback(() => {
    const trimmed = content.trim()
    if (!trimmed || isSending) return
    onSend(trimmed, model)
    setContent('')
    // Сбрасываем высоту textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
  }, [content, model, isSending, onSend])

  // Обработка клавиш — Enter отправляет, Shift+Enter — перенос строки
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault()
        handleSend()
      }
    },
    [handleSend],
  )

  // Обновление текста + ресайз
  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      setContent(e.target.value)
      adjustTextareaHeight()
    },
    [adjustTextareaHeight],
  )

  const canSend = content.trim().length > 0 && !isSending

  return (
    <div className="border-t bg-white p-4">
      <div className="mx-auto flex max-w-3xl items-end gap-3">
        {/* Селектор модели — фиксированная ширина */}
        <ModelSelector value={model} onChange={setModel} />

        {/* Textarea с авто-ресайзом */}
        <textarea
          ref={textareaRef}
          value={content}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder="Type your message..."
          maxLength={MAX_MESSAGE_LENGTH}
          disabled={isSending}
          rows={1}
          className="flex-1 resize-none rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
          style={{ minHeight: '40px', maxHeight: '120px' }}
        />

        {/* Круглая кнопка отправки */}
        <Button
          onClick={handleSend}
          disabled={!canSend}
          size="icon"
          className="h-10 w-10 shrink-0 rounded-full"
        >
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}

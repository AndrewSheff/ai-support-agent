import { Bot } from 'lucide-react'

/**
 * Индикатор набора — три прыгающие точки, чтоб юзер видел, что AI думает.
 * Классы bounce-dot-* определены в globals.css.
 */
export function TypingIndicator() {
  return (
    <div className="flex items-start gap-3 px-4 py-3">
      {/* Аватарка AI — как и в обычном сообщении */}
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-white">
        <Bot className="h-4 w-4" />
      </div>

      <div className="flex items-center gap-2 rounded-lg bg-slate-100 px-4 py-3">
        {/* Три точки с разной задержкой анимации */}
        <span className="bounce-dot-1 h-2 w-2 rounded-full bg-slate-400" />
        <span className="bounce-dot-2 h-2 w-2 rounded-full bg-slate-400" />
        <span className="bounce-dot-3 h-2 w-2 rounded-full bg-slate-400" />
        <span className="ml-1 text-sm text-slate-500">Thinking...</span>
      </div>
    </div>
  )
}

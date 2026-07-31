import { MessageSquare, HelpCircle, Search, BookOpen } from 'lucide-react'

/** Пропсы экрана приветствия */
interface WelcomeScreenProps {
  onQuickAction: (text: string) => void
}

/** Карточки быстрых действий — юзер тыкает и сразу начинает чат */
const quickActions = [
  {
    icon: HelpCircle,
    text: 'What can this system do?',
    description: 'Learn about available features',
  },
  {
    icon: Search,
    text: 'Help me find information',
    description: 'Search through documents',
  },
  {
    icon: BookOpen,
    text: 'Explain a concept',
    description: 'Get a detailed explanation',
  },
]

/**
 * Экран приветствия — показываем, когда юзер ещё не выбрал разговор.
 * Три карточки быстрого старта, клик создает новый чат.
 */
export function WelcomeScreen({ onQuickAction }: WelcomeScreenProps) {
  return (
    <div className="flex h-full flex-col items-center justify-center px-4">
      {/* Иконка и заголовок */}
      <MessageSquare className="mb-4 h-12 w-12 text-slate-300" />
      <h2 className="mb-8 text-2xl font-semibold text-slate-700">
        How can I help you today?
      </h2>

      {/* Карточки быстрого старта */}
      <div className="grid w-full max-w-2xl grid-cols-1 gap-3 md:grid-cols-3">
        {quickActions.map((action) => (
          <button
            key={action.text}
            onClick={() => onQuickAction(action.text)}
            className="flex flex-col items-center gap-2 rounded-lg border border-slate-200 bg-white p-4 text-center transition-colors hover:border-primary/30 hover:bg-primary/5"
          >
            <action.icon className="h-6 w-6 text-slate-400" />
            <span className="text-sm font-medium text-slate-700">
              {action.text}
            </span>
            <span className="text-xs text-slate-500">{action.description}</span>
          </button>
        ))}
      </div>
    </div>
  )
}

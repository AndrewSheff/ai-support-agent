import { useCallback } from 'react'
import { Sparkles } from 'lucide-react'
import { MODELS } from '@/lib/constants'
import type { ModelKey } from '@/lib/constants'

/** Пропсы для селектора модели */
interface ModelSelectorProps {
  value: ModelKey
  onChange: (model: ModelKey) => void
}

/**
 * Компактный селектор модели — Claude или GPT.
 * Сохраняет выбор в localStorage, чтоб юзер не выбирал каждый раз.
 */
export function ModelSelector({ value, onChange }: ModelSelectorProps) {
  // При смене модели обновляем и стейт, и localStorage
  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLSelectElement>) => {
      const model = e.target.value as ModelKey
      localStorage.setItem('preferred_model', model)
      onChange(model)
    },
    [onChange],
  )

  return (
    <div className="relative flex items-center">
      <Sparkles className="pointer-events-none absolute left-2.5 h-4 w-4 text-slate-400" />
      <select
        value={value}
        onChange={handleChange}
        className="h-9 w-[120px] cursor-pointer appearance-none rounded-md border border-input bg-background py-1 pl-8 pr-3 text-sm shadow-sm focus:outline-none focus:ring-1 focus:ring-ring"
      >
        {(Object.entries(MODELS) as [ModelKey, string][]).map(([key, label]) => (
          <option key={key} value={key}>
            {label}
          </option>
        ))}
      </select>
    </div>
  )
}

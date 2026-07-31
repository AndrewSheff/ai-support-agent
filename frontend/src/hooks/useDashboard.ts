import { useQuery } from '@tanstack/react-query'
import { getActivity, getStats, getTopQuestions } from '@/api/dashboard'

/**
 * Хук для статистики дашборда — кешируем на минуту, рефетчим при фокусе окна
 */
export function useStats(period: string) {
  return useQuery({
    queryKey: ['dashboard', 'stats', period],
    queryFn: () => getStats(period),
    staleTime: 60000,
    refetchOnWindowFocus: true,
  })
}

/**
 * Хук для графика активности — тоже кешируем на минуту
 */
export function useActivity(period: string) {
  return useQuery({
    queryKey: ['dashboard', 'activity', period],
    queryFn: () => getActivity(period),
    staleTime: 60000,
  })
}

/**
 * Хук для топа вопросов — кеш на минуту
 */
export function useTopQuestions() {
  return useQuery({
    queryKey: ['dashboard', 'top-questions'],
    queryFn: () => getTopQuestions(),
    staleTime: 60000,
  })
}

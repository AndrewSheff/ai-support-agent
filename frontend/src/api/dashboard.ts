import type { ActivityItem, StatsResponse, TopQuestion } from '@/types'
import apiClient from './client'

/**
 * Статистика дашборда — юзеры, документы, вопросы за период
 */
export async function getStats(period?: string): Promise<StatsResponse> {
  const { data } = await apiClient.get<StatsResponse>('/dashboard/stats', {
    params: { period },
  })
  return data
}

/**
 * Активность по дням — сколько вопросов задали за период
 */
export async function getActivity(period?: string): Promise<{ data: ActivityItem[] }> {
  const { data } = await apiClient.get<{ data: ActivityItem[] }>('/dashboard/activity', {
    params: { period },
  })
  return data
}

/**
 * Топ вопросов — самые популярные запросы юзеров
 */
export async function getTopQuestions(): Promise<{ items: TopQuestion[] }> {
  const { data } = await apiClient.get<{ items: TopQuestion[] }>('/dashboard/top-questions')
  return data
}

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { createConversation, deleteConversation, getConversations } from '@/api/chat'

/**
 * Хук для списка бесед — подтягивает с поиском, кеш не храним (staleTime: 0)
 */
export function useConversations(search?: string) {
  return useQuery({
    queryKey: ['conversations', search],
    queryFn: () => getConversations({ search }),
    staleTime: 0,
  })
}

/**
 * Хук для создания новой беседы — после успеха инвалидируем список
 */
export function useCreateConversation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (title: string | undefined) => createConversation(title),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['conversations'] })
    },
  })
}

/**
 * Хук для удаления беседы — после успеха тоже обновляем список
 */
export function useDeleteConversation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => deleteConversation(id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['conversations'] })
    },
  })
}

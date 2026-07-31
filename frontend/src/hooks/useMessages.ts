import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { getConversation, sendMessage } from '@/api/chat'

/**
 * Хук для загрузки конкретной беседы с сообщениями.
 * Не грузим, пока id не передан (enabled: !!id).
 */
export function useConversation(id: string) {
  return useQuery({
    queryKey: ['conversation', id],
    queryFn: () => getConversation(id),
    staleTime: 0,
    enabled: !!id,
  })
}

/** Параметры для отправки сообщения */
interface SendMessageVars {
  conversationId: string
  content: string
  model: string
}

/**
 * Хук для отправки сообщения — после успеха обновляем и беседу, и список бесед
 */
export function useSendMessage() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (vars: SendMessageVars) =>
      sendMessage(vars.conversationId, vars.content, vars.model),
    onSuccess: (_data, vars) => {
      void queryClient.invalidateQueries({ queryKey: ['conversation', vars.conversationId] })
      void queryClient.invalidateQueries({ queryKey: ['conversations'] })
    },
  })
}

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { deleteDocument, getDocuments, uploadDocument } from '@/api/documents'

/**
 * Хук для списка документов — если есть processing-документы, поллим каждые 5 сек
 */
export function useDocuments(status?: string, page?: number) {
  return useQuery({
    queryKey: ['documents', status, page],
    queryFn: () => getDocuments({ status, page }),
    staleTime: 30000,
    refetchInterval: (query) => {
      // Если среди документов есть обрабатываемые — поллим почаще
      const hasProcessing = query.state.data?.items.some((doc) => doc.status === 'processing')
      return hasProcessing ? 5000 : false
    },
  })
}

/**
 * Хук для загрузки документа — после успеха обновляем список
 */
export function useUploadDocument() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (file: File) => uploadDocument(file),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['documents'] })
    },
  })
}

/**
 * Хук для удаления документа — после успеха обновляем список
 */
export function useDeleteDocument() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => deleteDocument(id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['documents'] })
    },
  })
}

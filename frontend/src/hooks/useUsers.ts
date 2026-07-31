import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { createUser, deleteUser, getUsers, updateUser } from '@/api/users'

/**
 * Хук для списка юзеров с пагинацией — кеш на минуту
 */
export function useUsers(page?: number) {
  return useQuery({
    queryKey: ['users', page],
    queryFn: () => getUsers({ page }),
    staleTime: 60000,
  })
}

/**
 * Хук для создания юзера — после успеха обновляем список
 */
export function useCreateUser() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: { email: string; name: string; role: string }) => createUser(data),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['users'] })
    },
  })
}

/** Параметры для обновления юзера */
interface UpdateUserVars {
  id: string
  data: Partial<{ name: string; role: string; is_active: boolean }>
}

/**
 * Хук для обновления юзера — после успеха обновляем список
 */
export function useUpdateUser() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (vars: UpdateUserVars) => updateUser(vars.id, vars.data),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['users'] })
    },
  })
}

/**
 * Хук для удаления юзера — после успеха обновляем список
 */
export function useDeleteUser() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => deleteUser(id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['users'] })
    },
  })
}

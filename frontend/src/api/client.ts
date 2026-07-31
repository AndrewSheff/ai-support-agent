import axios from 'axios'

/**
 * Базовый Axios-инстанс для общения с бэком.
 * Все запросы летят через /api/v1, токен цепляется автоматически.
 */
const apiClient = axios.create({
  baseURL: '/api/v1',
})

// Перехватчик запросов — подкидываем токен из localStorage
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Перехватчик ответов — если 401, значит сессия протухла, выкидываем на логин
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  },
)

export default apiClient

export const API_URL = '/api/v1'

export const MODELS = {
  claude: 'Claude',
  gpt: 'GPT',
} as const

export type ModelKey = keyof typeof MODELS

export const MAX_MESSAGE_LENGTH = 4000
export const MAX_FILE_SIZE = 50 * 1024 * 1024 // 50MB
export const ALLOWED_FILE_TYPES = ['.pdf', '.docx', '.txt']
export const ALLOWED_MIME_TYPES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'text/plain',
]

export const ITEMS_PER_PAGE = 20
export const CONVERSATIONS_PER_PAGE = 50

export const TOAST_DURATION = 4000
export const SEARCH_DEBOUNCE_MS = 300
export const PROCESSING_POLL_INTERVAL = 5000

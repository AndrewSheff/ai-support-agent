import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'
import { format, formatDistanceToNow, isToday, isYesterday } from 'date-fns'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: string | Date): string {
  return format(new Date(date), 'MMM d, yyyy')
}

export function formatTime(date: string | Date): string {
  return format(new Date(date), 'h:mm a')
}

export function formatRelativeTime(date: string | Date): string {
  const d = new Date(date)
  if (isToday(d)) {
    return formatDistanceToNow(d, { addSuffix: true })
  }
  if (isYesterday(d)) {
    return 'Yesterday'
  }
  return format(d, 'MMM d')
}

export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export function truncate(str: string, maxLen: number): string {
  if (str.length <= maxLen) return str
  return str.slice(0, maxLen) + '...'
}

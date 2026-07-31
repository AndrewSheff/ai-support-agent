import { useState, useRef, useCallback, type DragEvent, type ChangeEvent } from 'react'
import {
  Upload,
  FileText,
  File,
  FileType,
  Trash2,
  CloudUpload,
  ChevronLeft,
  ChevronRight,
  Loader2,
} from 'lucide-react'
import { toast } from 'sonner'
import { useDocuments, useUploadDocument, useDeleteDocument } from '@/hooks/useDocuments'
import { MAX_FILE_SIZE, ALLOWED_FILE_TYPES, ALLOWED_MIME_TYPES } from '@/lib/constants'
import { formatFileSize, formatRelativeTime, cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Progress } from '@/components/ui/progress'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import type { Document } from '@/types'

/** Фильтры для статуса документов */
const STATUS_FILTERS = [
  { value: undefined, label: 'All' },
  { value: 'indexed', label: 'Indexed' },
  { value: 'processing', label: 'Processing' },
  { value: 'error', label: 'Error' },
] as const

/**
 * Страница управления документами — загрузка, просмотр, удаление.
 * Тут админ крутит свою базу знаний: кидает файлы, следит за индексацией.
 */
export default function DocumentsPage() {
  const [statusFilter, setStatusFilter] = useState<string | undefined>(undefined)
  const [page, setPage] = useState(1)
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false)
  const [deleteTarget, setDeleteTarget] = useState<Document | null>(null)

  const { data, isLoading } = useDocuments(statusFilter, page)
  const deleteDocument = useDeleteDocument()

  const documents = data?.items ?? []
  const totalPages = data?.pages ?? 1

  /** Удаляем документ с тостом */
  const handleDelete = async () => {
    if (!deleteTarget) return
    try {
      await deleteDocument.mutateAsync(deleteTarget.id)
      toast.success('Document deleted')
    } catch {
      toast.error('Failed to delete document')
    } finally {
      setDeleteTarget(null)
    }
  }

  // Сбрасываем страницу при смене фильтра
  const handleFilterChange = (value: string | undefined) => {
    setStatusFilter(value)
    setPage(1)
  }

  return (
    <div className="p-6 space-y-6">
      {/* Шапка — заголовок и кнопка загрузки */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Documents</h1>
        <Button onClick={() => setUploadDialogOpen(true)}>
          <Upload className="h-4 w-4" />
          Upload Document
        </Button>
      </div>

      {/* Фильтры по статусу */}
      <div className="flex gap-2">
        {STATUS_FILTERS.map((filter) => (
          <button
            key={filter.label}
            onClick={() => handleFilterChange(filter.value)}
            className={cn(
              'rounded-md px-3 py-1.5 text-sm font-medium transition-colors',
              statusFilter === filter.value
                ? 'bg-primary text-white'
                : 'bg-white text-muted-foreground border hover:bg-slate-50',
            )}
          >
            {filter.label}
          </button>
        ))}
      </div>

      {/* Таблица документов (div-based) */}
      <div className="rounded-lg border bg-white">
        {/* Шапка таблицы */}
        <div className="grid grid-cols-[1fr_80px_80px_100px_70px_100px_50px] gap-4 border-b px-4 py-3 text-sm font-medium text-muted-foreground">
          <span>Name</span>
          <span>Type</span>
          <span>Size</span>
          <span>Status</span>
          <span>Chunks</span>
          <span>Uploaded</span>
          <span />
        </div>

        {/* Контент таблицы */}
        {isLoading ? (
          <div className="p-4 space-y-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}
          </div>
        ) : documents.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <FileText className="h-12 w-12 text-slate-300 mb-4" />
            <p className="text-lg font-medium text-slate-600">No documents yet</p>
            <p className="mt-1 text-sm text-muted-foreground">
              Upload your first document to get started
            </p>
            <Button
              className="mt-4"
              onClick={() => setUploadDialogOpen(true)}
            >
              <Upload className="h-4 w-4" />
              Upload your first document
            </Button>
          </div>
        ) : (
          documents.map((doc) => (
            <div
              key={doc.id}
              className="grid grid-cols-[1fr_80px_80px_100px_70px_100px_50px] gap-4 items-center border-b last:border-b-0 px-4 py-3 text-sm hover:bg-slate-50 transition-colors"
            >
              {/* Имя файла с иконкой */}
              <div className="flex items-center gap-2 min-w-0">
                <DocumentIcon fileType={doc.file_type} />
                <span className="truncate" title={doc.original_name}>
                  {doc.original_name}
                </span>
              </div>

              {/* Тип файла */}
              <div>
                <Badge variant="outline" className="uppercase text-xs">
                  {doc.file_type}
                </Badge>
              </div>

              {/* Размер */}
              <span className="text-muted-foreground">
                {formatFileSize(doc.file_size)}
              </span>

              {/* Статус */}
              <div>
                <StatusBadge status={doc.status} />
              </div>

              {/* Количество чанков */}
              <span className="text-muted-foreground">
                {doc.chunk_count}
              </span>

              {/* Дата загрузки */}
              <span className="text-muted-foreground">
                {formatRelativeTime(doc.created_at)}
              </span>

              {/* Кнопка удаления */}
              <div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setDeleteTarget(doc)}
                  className="text-muted-foreground hover:text-destructive"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Пагинация */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page <= 1}
          >
            <ChevronLeft className="h-4 w-4" />
            Previous
          </Button>
          <span className="px-3 text-sm text-muted-foreground">
            Page {page} of {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page >= totalPages}
          >
            Next
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      )}

      {/* Диалог загрузки документа */}
      <UploadDialog
        open={uploadDialogOpen}
        onOpenChange={setUploadDialogOpen}
      />

      {/* Алерт-диалог подтверждения удаления */}
      <AlertDialog
        open={!!deleteTarget}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Document</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete &quot;{deleteTarget?.original_name}&quot;?
              This action cannot be undone. All associated chunks will be removed.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {deleteDocument.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Deleting...
                </>
              ) : (
                'Delete'
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}

/**
 * Иконка документа по типу файла — разная для pdf, docx, txt.
 * Мелочь, а приятно.
 */
function DocumentIcon({ fileType }: { fileType: string }) {
  switch (fileType) {
    case 'pdf':
      return <FileText className="h-5 w-5 shrink-0 text-red-500" />
    case 'docx':
      return <File className="h-5 w-5 shrink-0 text-blue-500" />
    case 'txt':
      return <FileType className="h-5 w-5 shrink-0 text-slate-500" />
    default:
      return <File className="h-5 w-5 shrink-0 text-slate-400" />
  }
}

/**
 * Бейдж статуса документа — цвет зависит от статуса.
 * processing пульсирует, чтоб было видно что идет работа.
 */
function StatusBadge({ status }: { status: Document['status'] }) {
  const config = {
    indexed: { className: 'bg-green-100 text-green-700', label: 'Indexed' },
    processing: {
      className: 'bg-yellow-100 text-yellow-700 animate-pulse',
      label: 'Processing',
    },
    error: { className: 'bg-red-100 text-red-700', label: 'Error' },
    uploaded: { className: 'bg-slate-100 text-slate-600', label: 'Uploaded' },
  } as const

  const { className, label } = config[status]

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium',
        className,
      )}
    >
      {label}
    </span>
  )
}

/** Пропсы для диалога загрузки */
interface UploadDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

/**
 * Диалог загрузки документа — drag & drop зона, валидация, прогресс.
 * Принимает .pdf, .docx, .txt до 50MB.
 */
function UploadDialog({ open, onOpenChange }: UploadDialogProps) {
  const [isDragOver, setIsDragOver] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const uploadDocument = useUploadDocument()

  /** Валидация файла на клиенте — тип и размер */
  const validateFile = useCallback((file: File): string | null => {
    const extension = '.' + file.name.split('.').pop()?.toLowerCase()
    if (
      !ALLOWED_FILE_TYPES.includes(extension) &&
      !ALLOWED_MIME_TYPES.includes(file.type)
    ) {
      return `Unsupported file type. Allowed: ${ALLOWED_FILE_TYPES.join(', ')}`
    }
    if (file.size > MAX_FILE_SIZE) {
      return `File too large. Maximum size: ${formatFileSize(MAX_FILE_SIZE)}`
    }
    return null
  }, [])

  /** Обработка выбранного файла — валидируем и шлем на сервер */
  const handleFile = useCallback(
    async (file: File) => {
      const error = validateFile(file)
      if (error) {
        toast.error(error)
        return
      }

      // Имитируем прогресс, пока грузится
      setUploadProgress(10)
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => Math.min(prev + 15, 85))
      }, 500)

      try {
        await uploadDocument.mutateAsync(file)
        setUploadProgress(100)
        toast.success(`"${file.name}" uploaded successfully`)
        // Закрываем через секунду, чтоб юзер увидел 100%
        setTimeout(() => {
          onOpenChange(false)
          setUploadProgress(0)
        }, 800)
      } catch {
        toast.error('Failed to upload document')
        setUploadProgress(0)
      } finally {
        clearInterval(progressInterval)
      }
    },
    [uploadDocument, validateFile, onOpenChange],
  )

  /** Drop-обработчик — ловим файл из drag & drop */
  const handleDrop = useCallback(
    (e: DragEvent<HTMLDivElement>) => {
      e.preventDefault()
      setIsDragOver(false)
      const file = e.dataTransfer.files[0]
      if (file) void handleFile(file)
    },
    [handleFile],
  )

  /** Выбор файла через input */
  const handleInputChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0]
      if (file) void handleFile(file)
      // Сбрасываем input, чтоб можно было загрузить тот же файл повторно
      e.target.value = ''
    },
    [handleFile],
  )

  const isUploading = uploadDocument.isPending || uploadProgress > 0

  return (
    <Dialog open={open} onOpenChange={(v) => !isUploading && onOpenChange(v)}>
      <DialogContent className="sm:max-w-[480px]">
        <DialogHeader>
          <DialogTitle>Upload Document</DialogTitle>
          <DialogDescription>
            Upload a document to add it to the knowledge base. Supported formats: PDF, DOCX, TXT.
          </DialogDescription>
        </DialogHeader>

        {/* Зона drag & drop */}
        <div
          onDragOver={(e) => {
            e.preventDefault()
            setIsDragOver(true)
          }}
          onDragLeave={() => setIsDragOver(false)}
          onDrop={handleDrop}
          onClick={() => !isUploading && fileInputRef.current?.click()}
          className={cn(
            'flex flex-col items-center justify-center gap-3 rounded-lg border-2 border-dashed p-8 cursor-pointer transition-colors',
            isDragOver
              ? 'border-primary bg-primary/5'
              : 'border-slate-200 hover:border-slate-300',
            isUploading && 'pointer-events-none opacity-60',
          )}
        >
          {isUploading ? (
            <>
              <Loader2 className="h-10 w-10 animate-spin text-primary" />
              <p className="text-sm font-medium">Uploading...</p>
              <div className="w-full max-w-[200px]">
                <Progress value={uploadProgress} />
              </div>
            </>
          ) : (
            <>
              <CloudUpload className="h-10 w-10 text-slate-400" />
              <div className="text-center">
                <p className="text-sm font-medium">
                  Drag & drop files here or click to browse
                </p>
                <p className="mt-1 text-xs text-muted-foreground">
                  PDF, DOCX or TXT up to {formatFileSize(MAX_FILE_SIZE)}
                </p>
              </div>
            </>
          )}
        </div>

        {/* Скрытый input для выбора файла */}
        <input
          ref={fileInputRef}
          type="file"
          accept={ALLOWED_FILE_TYPES.join(',')}
          onChange={handleInputChange}
          className="hidden"
        />
      </DialogContent>
    </Dialog>
  )
}

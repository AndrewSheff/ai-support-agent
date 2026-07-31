import { useState } from 'react'
import {
  Users,
  FileText,
  MessageSquare,
  HelpCircle,
  ArrowUp,
  ArrowDown,
} from 'lucide-react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Area,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts'
import { format } from 'date-fns'
import { useStats, useActivity, useTopQuestions } from '@/hooks/useDashboard'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

/** Варианты периода для переключалки на дашборде */
const PERIODS = [
  { value: '1', label: 'Today' },
  { value: '7', label: '7 Days' },
  { value: '30', label: '30 Days' },
] as const

/**
 * Главная страница дашборда — статистика, график активности, топ вопросов.
 * Тут собрана вся аналитика для админа, чтоб было понятно что происходит.
 */
export default function DashboardPage() {
  const [period, setPeriod] = useState('7')

  const { data: stats, isLoading: statsLoading } = useStats(period)
  const { data: activityData, isLoading: activityLoading } = useActivity(period)
  const { data: topQuestionsData, isLoading: topQuestionsLoading } = useTopQuestions()

  // Массив точек для графика
  const chartData = activityData?.data ?? []
  // Список топ-вопросов
  const topQuestions = topQuestionsData?.items ?? []

  return (
    <div className="p-6 space-y-6">
      {/* Шапка — заголовок и переключатель периода */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-2xl font-bold">Dashboard</h1>

        {/* Переключалка периода — выглядит как tabs/toggle */}
        <div className="flex rounded-lg border bg-white p-1">
          {PERIODS.map((p) => (
            <button
              key={p.value}
              onClick={() => setPeriod(p.value)}
              className={cn(
                'rounded-md px-3 py-1.5 text-sm font-medium transition-colors',
                period === p.value
                  ? 'bg-primary text-primary-foreground shadow-sm'
                  : 'text-muted-foreground hover:text-foreground',
              )}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* Карточки статистики — 4 штуки в ряд */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Users"
          value={stats?.total_users}
          icon={<Users className="h-5 w-5" />}
          color="blue"
          isLoading={statsLoading}
        />
        <StatCard
          title="Documents"
          value={stats?.total_documents}
          subtitle={
            stats ? `${stats.indexed_documents} indexed` : undefined
          }
          icon={<FileText className="h-5 w-5" />}
          color="green"
          isLoading={statsLoading}
        />
        <StatCard
          title="Conversations"
          value={stats?.total_conversations}
          icon={<MessageSquare className="h-5 w-5" />}
          color="purple"
          isLoading={statsLoading}
        />
        <StatCard
          title="Questions"
          value={stats?.questions_in_period}
          changePercent={stats?.questions_change_percent}
          icon={<HelpCircle className="h-5 w-5" />}
          color="orange"
          isLoading={statsLoading}
        />
      </div>

      {/* Нижняя часть — график и топ вопросов */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* График активности */}
        <Card>
          <CardHeader>
            <CardTitle>Activity</CardTitle>
          </CardHeader>
          <CardContent>
            {activityLoading ? (
              <Skeleton className="h-[300px] w-full" />
            ) : chartData.length === 0 ? (
              <div className="flex h-[300px] items-center justify-center text-muted-foreground">
                No activity data for this period
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis
                    dataKey="date"
                    tickFormatter={(date: string) =>
                      format(new Date(date), 'MMM d')
                    }
                    tick={{ fontSize: 12 }}
                    stroke="#94a3b8"
                  />
                  <YAxis
                    tick={{ fontSize: 12 }}
                    stroke="#94a3b8"
                    allowDecimals={false}
                  />
                  <Tooltip
                    labelFormatter={(date: string) =>
                      format(new Date(date), 'MMM d, yyyy')
                    }
                    contentStyle={{
                      borderRadius: '8px',
                      border: '1px solid #e2e8f0',
                      boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
                    }}
                  />
                  <defs>
                    <linearGradient id="colorQuestions" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="hsl(222.2, 47.4%, 11.2%)" stopOpacity={0.1} />
                      <stop offset="95%" stopColor="hsl(222.2, 47.4%, 11.2%)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <Area
                    type="monotone"
                    dataKey="questions"
                    stroke="hsl(222.2, 47.4%, 11.2%)"
                    fill="url(#colorQuestions)"
                  />
                  <Line
                    type="monotone"
                    dataKey="questions"
                    stroke="hsl(222.2, 47.4%, 11.2%)"
                    strokeWidth={2}
                    dot={{ r: 4, fill: 'hsl(222.2, 47.4%, 11.2%)' }}
                    activeDot={{ r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        {/* Топ вопросов */}
        <Card>
          <CardHeader>
            <CardTitle>Top Questions</CardTitle>
          </CardHeader>
          <CardContent>
            {topQuestionsLoading ? (
              <div className="space-y-4">
                {Array.from({ length: 5 }).map((_, i) => (
                  <Skeleton key={i} className="h-8 w-full" />
                ))}
              </div>
            ) : topQuestions.length === 0 ? (
              <div className="flex h-[260px] items-center justify-center text-muted-foreground">
                No questions yet
              </div>
            ) : (
              <ol className="space-y-3">
                {topQuestions.slice(0, 5).map((q, index) => (
                  <li
                    key={index}
                    className="flex items-start gap-3 rounded-md p-2 hover:bg-slate-50"
                  >
                    {/* Номер вопроса в кружочке */}
                    <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary/10 text-xs font-semibold text-primary">
                      {index + 1}
                    </span>
                    <span className="flex-1 text-sm leading-snug">
                      {q.question}
                    </span>
                    <Badge variant="secondary" className="shrink-0">
                      {q.count}
                    </Badge>
                  </li>
                ))}
              </ol>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

/** Цвета для иконок stat-карточек */
const ICON_COLORS = {
  blue: 'bg-blue-100 text-blue-600',
  green: 'bg-green-100 text-green-600',
  purple: 'bg-purple-100 text-purple-600',
  orange: 'bg-orange-100 text-orange-600',
} as const

/** Пропсы для карточки статистики */
interface StatCardProps {
  title: string
  value: number | undefined
  subtitle?: string
  changePercent?: number | null
  icon: React.ReactNode
  color: keyof typeof ICON_COLORS
  isLoading: boolean
}

/**
 * Карточка статистики — иконка, число, подпись и опциональный процент изменения.
 * Ничего сложного, просто красивый блок с данными.
 */
function StatCard({
  title,
  value,
  subtitle,
  changePercent,
  icon,
  color,
  isLoading,
}: StatCardProps) {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-muted-foreground">
            {title}
          </span>
          <div
            className={cn(
              'flex h-9 w-9 items-center justify-center rounded-lg',
              ICON_COLORS[color],
            )}
          >
            {icon}
          </div>
        </div>

        <div className="mt-3">
          {isLoading ? (
            <Skeleton className="h-8 w-20" />
          ) : (
            <p className="text-2xl font-bold">{value ?? 0}</p>
          )}
        </div>

        {/* Подпись или процент изменения */}
        {!isLoading && (subtitle || changePercent != null) && (
          <div className="mt-1 flex items-center gap-1.5 text-sm">
            {changePercent != null && (
              <span
                className={cn(
                  'inline-flex items-center gap-0.5 font-medium',
                  changePercent >= 0 ? 'text-green-600' : 'text-red-600',
                )}
              >
                {changePercent >= 0 ? (
                  <ArrowUp className="h-3.5 w-3.5" />
                ) : (
                  <ArrowDown className="h-3.5 w-3.5" />
                )}
                {Math.abs(changePercent)}%
              </span>
            )}
            {subtitle && (
              <span className="text-muted-foreground">{subtitle}</span>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

import React from 'react'
import { Report, ReportStatus } from '@shared/types/report'
import { ReportCard } from './ReportCard'

interface ReportsListProps {
  reports: Report[]
  loading: boolean
  error: string | null
  total: number
  limit: number
  offset: number
  currentStatus?: ReportStatus
  onExecute: (reportId: string) => void
  onEdit: (reportId: string) => void
  onDelete: (reportId: string) => void
  onLoadMore: () => void
  onStatusFilter: (status?: ReportStatus) => void
}

export const ReportsList: React.FC<ReportsListProps> = ({
  reports,
  loading,
  error,
  total,
  limit,
  offset,
  currentStatus,
  onExecute,
  onEdit,
  onDelete,
  onLoadMore,
  onStatusFilter,
}) => {
  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
        <p className="font-medium">Erro ao carregar relatórios</p>
        <p className="text-sm">{error}</p>
      </div>
    )
  }

  if (loading && reports.length === 0) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="bg-muted rounded-lg h-40 animate-pulse" />
        ))}
      </div>
    )
  }

  if (reports.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground text-lg">Nenhum relatório encontrado</p>
        <p className="text-sm text-gray-500 mt-2">Crie seu primeiro relatório para começar.</p>
      </div>
    )
  }

  const hasMore = offset + limit < total

  return (
    <div className="space-y-4">
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => onStatusFilter(undefined)}
          aria-pressed={currentStatus === undefined}
          className="px-3 py-1 bg-muted text-gray-700 rounded-full text-sm hover:bg-gray-300 transition cursor-pointer"
        >
          Todos
        </button>
        <button
          onClick={() => onStatusFilter(ReportStatus.ACTIVE)}
          aria-pressed={currentStatus === ReportStatus.ACTIVE}
          className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm hover:bg-green-200 transition cursor-pointer"
        >
          Ativos
        </button>
        <button
          onClick={() => onStatusFilter(ReportStatus.DRAFT)}
          aria-pressed={currentStatus === ReportStatus.DRAFT}
          className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm hover:bg-gray-200 transition cursor-pointer"
        >
          Rascunhos
        </button>
        <button
          onClick={() => onStatusFilter(ReportStatus.SCHEDULED)}
          aria-pressed={currentStatus === ReportStatus.SCHEDULED}
          className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm hover:bg-blue-200 transition cursor-pointer"
        >
          Agendados
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {reports.map((report) => (
          <ReportCard
            key={report.id}
            report={report}
            onExecute={onExecute}
            onEdit={onEdit}
            onDelete={onDelete}
            loading={loading}
          />
        ))}
      </div>

      {hasMore && (
        <div className="flex justify-center pt-6">
          <button
            onClick={onLoadMore}
            disabled={loading}
            className="px-6 py-2 bg-primary text-white rounded-md hover:bg-primary-dark disabled:bg-gray-400 transition cursor-pointer disabled:cursor-not-allowed"
          >
            {loading ? 'Carregando...' : 'Carregar mais'}
          </button>
        </div>
      )}

      <div className="text-center text-sm text-gray-600 pt-4">
        Exibindo {reports.length} de {total} relatórios
      </div>
    </div>
  )
}

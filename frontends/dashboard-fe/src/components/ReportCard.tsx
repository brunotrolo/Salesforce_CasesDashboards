import React from 'react'
import { Report, ReportStatus } from '@shared/types/report'
import { formatDistanceToNow } from 'date-fns'
import { ptBR } from 'date-fns/locale'

interface ReportCardProps {
  report: Report
  onExecute: (reportId: string) => void
  onEdit: (reportId: string) => void
  onDelete: (reportId: string) => void
  loading?: boolean
}

const statusColors: Record<ReportStatus, string> = {
  [ReportStatus.DRAFT]: 'bg-gray-100 text-gray-800',
  [ReportStatus.ACTIVE]: 'bg-green-100 text-green-800',
  [ReportStatus.SCHEDULED]: 'bg-blue-100 text-blue-800',
  [ReportStatus.PAUSED]: 'bg-yellow-100 text-yellow-800',
  [ReportStatus.ARCHIVED]: 'bg-gray-200 text-gray-700',
}

const statusLabels: Record<ReportStatus, string> = {
  [ReportStatus.DRAFT]: 'Rascunho',
  [ReportStatus.ACTIVE]: 'Ativo',
  [ReportStatus.SCHEDULED]: 'Agendado',
  [ReportStatus.PAUSED]: 'Pausado',
  [ReportStatus.ARCHIVED]: 'Arquivado',
}

export const ReportCard: React.FC<ReportCardProps> = ({
  report,
  onExecute,
  onEdit,
  onDelete,
  loading = false,
}) => {
  const status = (report.status || ReportStatus.DRAFT) as ReportStatus
  const createdAt = new Date(report.metadata.created_at)
  const timeAgo = formatDistanceToNow(createdAt, {
    addSuffix: true,
    locale: ptBR,
  })

  return (
    <div className="bg-card border border-border rounded-lg p-6 hover:border-primary transition-colors">
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900">{report.name}</h3>
          {report.description && (
            <p className="text-sm text-gray-600 mt-1">{report.description}</p>
          )}
        </div>
        <span
          className={`px-3 py-1 rounded-full text-sm font-medium whitespace-nowrap ml-4 ${
            statusColors[status]
          }`}
        >
          {statusLabels[status]}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4 text-sm text-gray-600">
        <div>
          <span className="text-gray-500">Objeto:</span>
          <p className="font-medium">{report.object_type}</p>
        </div>
        <div>
          <span className="text-gray-500">Campos:</span>
          <p className="font-medium">{report.fields.length}</p>
        </div>
        <div>
          <span className="text-gray-500">Tipo:</span>
          <p className="font-medium">{report.report_type}</p>
        </div>
        <div>
          <span className="text-gray-500">Criado:</span>
          <p className="font-medium text-xs">{timeAgo}</p>
        </div>
      </div>

      {report.filters && report.filters.length > 0 && (
        <div className="mb-4 pb-4 border-b border-gray-200">
          <span className="text-sm text-gray-500">Filtros: {report.filters.length}</span>
        </div>
      )}

      <div className="flex gap-2">
        <button
          onClick={() => onExecute(report.id)}
          disabled={loading || status === ReportStatus.DRAFT || status === ReportStatus.ARCHIVED}
          className="flex-1 px-4 py-2 bg-primary text-white rounded-md hover:bg-primary-dark disabled:bg-gray-400 disabled:cursor-not-allowed transition cursor-pointer"
        >
          Executar
        </button>
        <button
          onClick={() => onEdit(report.id)}
          disabled={loading}
          className="flex-1 px-4 py-2 bg-card border border-border text-gray-900 rounded-md hover:bg-muted disabled:opacity-50 transition cursor-pointer"
        >
          Editar
        </button>
        <button
          onClick={() => onDelete(report.id)}
          disabled={loading}
          className="flex-1 px-4 py-2 bg-card border border-border text-destructive rounded-md hover:bg-red-50 disabled:opacity-50 transition cursor-pointer"
        >
          Deletar
        </button>
      </div>
    </div>
  )
}

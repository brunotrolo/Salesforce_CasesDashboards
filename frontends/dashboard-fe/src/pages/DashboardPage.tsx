import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ReportsList } from '../components/ReportsList'
import { useReports } from '../hooks/useReports'
import type { ReportStatus } from '../types/report'

interface ConfirmDialogProps {
  open: boolean
  title: string
  message: string
  confirmLabel?: string
  onConfirm: () => void
  onCancel: () => void
}

const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
  open,
  title,
  message,
  confirmLabel = 'Deletar',
  onConfirm,
  onCancel,
}) => {
  if (!open) return null

  return (
    <div
      className="fixed inset-0 bg-black/40 flex items-center justify-center z-50"
      role="dialog"
      aria-modal="true"
      aria-labelledby="confirm-title"
    >
      <div className="bg-card border border-border rounded-lg p-6 max-w-md w-full mx-4">
        <h2 id="confirm-title" className="text-lg font-semibold text-gray-900 mb-2">
          {title}
        </h2>
        <p className="text-sm text-muted-foreground mb-6">{message}</p>
        <div className="flex justify-end gap-3">
          <button
            onClick={onCancel}
            autoFocus
            className="px-4 py-2 bg-card border border-border text-gray-700 rounded-md hover:bg-muted transition cursor-pointer"
          >
            Cancelar
          </button>
          <button
            onClick={onConfirm}
            className="px-4 py-2 bg-destructive text-white rounded-md hover:bg-red-700 transition cursor-pointer"
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  )
}

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate()
  const [currentStatus, setCurrentStatus] = useState<ReportStatus | undefined>()
  const [reportToDelete, setReportToDelete] = useState<string | null>(null)
  const {
    reports,
    loading,
    error,
    total,
    offset,
    limit,
    loadReports,
    executeReport,
    deleteReport,
    setPagination,
  } = useReports()

  useEffect(() => {
    loadReports(currentStatus)
  }, [currentStatus, loadReports])

  const handleExecute = async (reportId: string) => {
    try {
      const result = await executeReport(reportId)
      navigate(`/report/${reportId}/results`, { state: { data: result } })
    } catch (error) {
      console.error('Failed to execute report:', error)
    }
  }

  const handleEdit = (reportId: string) => {
    navigate(`/builder/${reportId}`)
  }

  const handleDeleteConfirm = async () => {
    if (!reportToDelete) return
    try {
      await deleteReport(reportToDelete)
    } catch (error) {
      console.error('Failed to delete report:', error)
    } finally {
      setReportToDelete(null)
    }
  }

  const handleLoadMore = () => {
    setPagination(offset + limit, limit)
    loadReports(currentStatus)
  }

  const handleStatusFilter = (status?: ReportStatus) => {
    setCurrentStatus(status)
    setPagination(0, limit)
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="bg-card border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-primary-dark">Relatórios Salesforce</h1>
              <p className="text-muted-foreground mt-1">Gerencie e execute seus relatórios</p>
            </div>
            <button
              onClick={() => navigate('/builder')}
              className="px-6 py-2 bg-primary text-white rounded-md hover:bg-primary-dark transition font-medium cursor-pointer"
            >
              Novo Relatório
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-card border border-border rounded-lg p-6">
          <ReportsList
            reports={reports}
            loading={loading}
            error={error}
            total={total}
            limit={limit}
            offset={offset}
            currentStatus={currentStatus}
            onExecute={handleExecute}
            onEdit={handleEdit}
            onDelete={setReportToDelete}
            onLoadMore={handleLoadMore}
            onStatusFilter={handleStatusFilter}
          />
        </div>
      </main>

      <ConfirmDialog
        open={reportToDelete !== null}
        title="Deletar relatório"
        message="Tem certeza que deseja deletar este relatório? Esta ação não pode ser desfeita."
        onConfirm={handleDeleteConfirm}
        onCancel={() => setReportToDelete(null)}
      />
    </div>
  )
}
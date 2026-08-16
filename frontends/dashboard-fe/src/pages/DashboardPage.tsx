import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ReportsList } from '@components/ReportsList'
import { useReports } from '@hooks/useReports'
import { ReportStatus } from '@types/report'

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate()
  const [currentStatus, setCurrentStatus] = useState<ReportStatus | undefined>()
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

  const handleDelete = async (reportId: string) => {
    if (window.confirm('Tem certeza que deseja deletar este relatório?')) {
      try {
        await deleteReport(reportId)
      } catch (error) {
        console.error('Failed to delete report:', error)
      }
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
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Relatórios Salesforce</h1>
              <p className="text-gray-600 mt-2">Gerencie e execute seus relatórios</p>
            </div>
            <button
              onClick={() => navigate('/builder')}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium"
            >
              Novo Relatório
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow p-6">
          <ReportsList
            reports={reports}
            loading={loading}
            error={error}
            total={total}
            limit={limit}
            offset={offset}
            onExecute={handleExecute}
            onEdit={handleEdit}
            onDelete={handleDelete}
            onLoadMore={handleLoadMore}
            onStatusFilter={handleStatusFilter}
          />
        </div>
      </main>
    </div>
  )
}

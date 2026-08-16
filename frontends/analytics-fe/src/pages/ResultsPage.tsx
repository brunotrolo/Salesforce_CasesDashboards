import React, { useState, useRef } from 'react'
import { useParams, useNavigate, useLocation } from 'react-router-dom'
import { BarChart } from '@components/BarChart'
import { DataTable } from '@components/DataTable'
import { ReportExecutionResult, Report } from '@types/report'
import { AnalyticsResult, TableData, ChartData } from '@types/analytics'
import { formatDuration, formatNumber } from '@utils/formatters'
import { exportToPDF, exportToExcel, exportToCSV, copyToClipboard } from '@utils/exporters'

interface LocationState {
  result: ReportExecutionResult
  report?: Report
}

export const ResultsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const location = useLocation()
  const [view, setView] = useState<'table' | 'charts'>('table')
  const [exportLoading, setExportLoading] = useState<string | null>(null)
  const [exportMessage, setExportMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)
  const chartRef = useRef<HTMLDivElement>(null)

  const result = (location.state as LocationState)?.result
  const report = (location.state as LocationState)?.report

  const handleExportPDF = async () => {
    setExportLoading('pdf')
    try {
      const analyticsResult: AnalyticsResult = {
        rows: result.rows_returned,
        execution_time: result.execution_time_ms,
        status: result.status,
        data: result.data
      }
      await exportToPDF(report?.name || 'Report', analyticsResult, chartRef.current || undefined)
      setExportMessage({ type: 'success', text: 'PDF exportado com sucesso' })
      setTimeout(() => setExportMessage(null), 3000)
    } catch (error) {
      console.error('Export PDF error:', error)
      setExportMessage({ type: 'error', text: 'Erro ao exportar PDF' })
      setTimeout(() => setExportMessage(null), 3000)
    } finally {
      setExportLoading(null)
    }
  }

  const handleExportExcel = () => {
    setExportLoading('excel')
    try {
      const analyticsResult: AnalyticsResult = {
        rows: result.rows_returned,
        execution_time: result.execution_time_ms,
        status: result.status,
        data: result.data
      }
      exportToExcel(report?.name || 'Report', analyticsResult, {
        execution_time_ms: result.execution_time_ms,
        rows_returned: result.rows_returned,
        executed_at: result.executed_at
      })
      setExportMessage({ type: 'success', text: 'Excel exportado com sucesso' })
      setTimeout(() => setExportMessage(null), 3000)
    } catch (error) {
      console.error('Export Excel error:', error)
      setExportMessage({ type: 'error', text: 'Erro ao exportar Excel' })
      setTimeout(() => setExportMessage(null), 3000)
    } finally {
      setExportLoading(null)
    }
  }

  const handleExportCSV = () => {
    setExportLoading('csv')
    try {
      exportToCSV(report?.name || 'Report', result.data)
      setExportMessage({ type: 'success', text: 'CSV exportado com sucesso' })
      setTimeout(() => setExportMessage(null), 3000)
    } catch (error) {
      console.error('Export CSV error:', error)
      setExportMessage({ type: 'error', text: 'Erro ao exportar CSV' })
      setTimeout(() => setExportMessage(null), 3000)
    } finally {
      setExportLoading(null)
    }
  }

  const handleCopyToClipboard = async () => {
    setExportLoading('clipboard')
    try {
      await copyToClipboard(result.data)
      setExportMessage({ type: 'success', text: 'Dados copiados para a área de transferência' })
      setTimeout(() => setExportMessage(null), 3000)
    } catch (error) {
      console.error('Copy to clipboard error:', error)
      setExportMessage({ type: 'error', text: 'Erro ao copiar dados' })
      setTimeout(() => setExportMessage(null), 3000)
    } finally {
      setExportLoading(null)
    }
  }
  if (!result) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center">
            <p className="text-gray-600 mb-4">Nenhum resultado para exibir</p>
            <button
              onClick={() => navigate('/dashboard')}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Voltar ao Dashboard
            </button>
          </div>
        </div>
      </div>
    )
  }

  const tableData: TableData = {
    columns: result.data.length > 0
      ? Object.keys(result.data[0]).map((key) => ({
          key,
          label: key,
          type: 'string' as const,
        }))
      : [],
    rows: result.data,
    total: result.rows_returned,
  }

  // Prepare chart data from first numeric field
  const chartData: ChartData[] = result.data.map((row, idx) => ({
    name: String(idx + 1),
    value: Object.values(row).find(v => typeof v === 'number') as number || 0,
    label: JSON.stringify(row),
  }))

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Resultados do Relatório
              </h1>
              {report && <p className="text-gray-600 mt-2">{report.name}</p>}
            </div>
            <button
              onClick={() => navigate('/dashboard')}
              className="px-4 py-2 text-gray-700 hover:text-gray-900 transition"
            >
              ← Voltar
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Summary cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-gray-600 text-sm">Total de Linhas</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">
              {formatNumber(result.rows_returned)}
            </p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-gray-600 text-sm">Tempo de Execução</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">
              {formatDuration(result.execution_time_ms)}
            </p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-gray-600 text-sm">Status</p>
            <p className={`text-3xl font-bold mt-2 ${
              result.status === 'success' ? 'text-green-600' : 'text-red-600'
            }`}>
              {result.status === 'success' ? '✓' : '✕'}
            </p>
          </div>
        </div>

        {/* View toggle */}
        <div className="mb-6 flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center">
          <div className="flex gap-2">
            <button
              onClick={() => setView('table')}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                view === 'table'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-900 hover:bg-gray-300'
              }`}
            >
              Tabela
            </button>
            <button
              onClick={() => setView('charts')}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                view === 'charts'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-900 hover:bg-gray-300'
              }`}
            >
              Gráficos
            </button>
          </div>

          {/* Export buttons */}
          <div className="flex gap-2 flex-wrap">
            <button
              onClick={handleExportPDF}
              disabled={exportLoading !== null}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition font-medium flex items-center gap-2"
            >
              {exportLoading === 'pdf' ? '⏳' : '📄'}
              PDF
            </button>
            <button
              onClick={handleExportExcel}
              disabled={exportLoading !== null}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition font-medium flex items-center gap-2"
            >
              {exportLoading === 'excel' ? '⏳' : '📊'}
              Excel
            </button>
            <button
              onClick={handleExportCSV}
              disabled={exportLoading !== null}
              className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 disabled:opacity-50 disabled:cursor-not-allowed transition font-medium flex items-center gap-2"
            >
              {exportLoading === 'csv' ? '⏳' : '📋'}
              CSV
            </button>
            <button
              onClick={handleCopyToClipboard}
              disabled={exportLoading !== null}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition font-medium flex items-center gap-2"
            >
              {exportLoading === 'clipboard' ? '⏳' : '📋'}
              Copiar
            </button>
          </div>
        </div>

        {/* Export message */}
        {exportMessage && (
          <div className={`mb-6 p-4 rounded-lg ${
            exportMessage.type === 'success'
              ? 'bg-green-100 text-green-800 border border-green-300'
              : 'bg-red-100 text-red-800 border border-red-300'
          }`}>
            {exportMessage.text}
          </div>
        )}
        {/* Content */}
        {view === 'table' ? (
          <DataTable data={tableData} maxRows={50} />
        ) : (
          <div className="space-y-8" ref={chartRef}>
            <BarChart
              data={chartData.slice(0, 10)}
              config={{
                type: 'bar',
                title: 'Distribuição de Valores',
                color: '#3b82f6',
              }}
            />
          </div>
        )}
      </main>
    </div>
  )
}

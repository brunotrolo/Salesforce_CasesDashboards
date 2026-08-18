import React, { useState, useRef } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { BarChart } from '@components/BarChart'
import { DataTable } from '@components/DataTable'
import { ReportExecutionResult, Report } from '@typings/report'
import { AnalyticsResult, TableData, ChartData } from '@typings/analytics'
import { formatDuration, formatNumber } from '@utils/formatters'
import { exportToPDF, exportToExcel, exportToCSV, copyToClipboard } from '@utils/exporters'

interface LocationState {
  result: ReportExecutionResult
  report?: Report
}

export const ResultsPage: React.FC = () => {
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
        report_id: result.report_id,
        report_name: report?.name || 'Report',
        executed_at: result.executed_at,
        execution_time_ms: result.execution_time_ms,
        rows_returned: result.rows_returned,
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
        report_id: result.report_id,
        report_name: report?.name || 'Report',
        executed_at: result.executed_at,
        execution_time_ms: result.execution_time_ms,
        rows_returned: result.rows_returned,
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
              className="px-6 py-2 bg-primary text-white rounded-md hover:bg-primary-dark cursor-pointer"
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
      <header className="bg-card border-b border-border">
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
          <div className="bg-card border border-border rounded-lg p-6">
            <p className="text-gray-600 text-sm">Total de Linhas</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">
              {formatNumber(result.rows_returned)}
            </p>
          </div>

          <div className="bg-card border border-border rounded-lg p-6">
            <p className="text-gray-600 text-sm">Tempo de Execução</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">
              {formatDuration(result.execution_time_ms)}
            </p>
          </div>

          <div className="bg-card border border-border rounded-lg p-6">
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
                  ? 'bg-primary text-white'
                  : 'bg-gray-200 text-gray-900 hover:bg-gray-300'
              }`}
            >
              Tabela
            </button>
            <button
              onClick={() => setView('charts')}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                view === 'charts'
                  ? 'bg-primary text-white'
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
              {exportLoading === 'pdf' ? (
                <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24" aria-hidden="true">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
                </svg>
              ) : (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  <path strokeLinecap="round" strokeLinejoin="round" d="M17 21v-8H9v8M9 10h6" />
                </svg>
              )}
              PDF
            </button>
            <button
              onClick={handleExportExcel}
              disabled={exportLoading !== null}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition font-medium flex items-center gap-2"
            >
              {exportLoading === 'excel' ? (
                <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24" aria-hidden="true">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
                </svg>
              ) : (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" aria-hidden="true">
                  <rect x="3" y="3" width="18" height="18" rx="2" />
                  <path strokeLinecap="round" strokeLinejoin="round" d="M7 16l4-6-4-6M11 16h6M17 10h.01" />
                </svg>
              )}
              Excel
            </button>
            <button
              onClick={handleExportCSV}
              disabled={exportLoading !== null}
              className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 disabled:opacity-50 disabled:cursor-not-allowed transition font-medium flex items-center gap-2"
            >
              {exportLoading === 'csv' ? (
                <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24" aria-hidden="true">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
                </svg>
              ) : (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6M9 16h6M9 8h6M5 3h14a2 2 0 012 2v14a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2z" />
                </svg>
              )}
              CSV
            </button>
            <button
              onClick={handleCopyToClipboard}
              disabled={exportLoading !== null}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition font-medium flex items-center gap-2"
            >
              {exportLoading === 'clipboard' ? (
                <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24" aria-hidden="true">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
                </svg>
              ) : (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" aria-hidden="true">
                  <rect x="8" y="8" width="12" height="12" rx="2" />
                  <path strokeLinecap="round" strokeLinejoin="round" d="M16 8V6a2 2 0 00-2-2H6a2 2 0 00-2 2v8a2 2 0 002 2h2" />
                </svg>
              )}
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

import React, { useState } from 'react'
import { useParams, useNavigate, useLocation } from 'react-router-dom'
import { BarChart } from '@components/BarChart'
import { DataTable } from '@components/DataTable'
import { ReportExecutionResult, Report } from '@types/report'
import { AnalyticsResult, TableData, ChartData } from '@types/analytics'
import { formatDuration, formatNumber } from '@utils/formatters'

interface LocationState {
  result: ReportExecutionResult
  report?: Report
}

export const ResultsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const location = useLocation()
  const [view, setView] = useState<'table' | 'charts'>('table')

  const result = (location.state as LocationState)?.result
  const report = (location.state as LocationState)?.report

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
        <div className="mb-6 flex gap-2">
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

        {/* Content */}
        {view === 'table' ? (
          <DataTable data={tableData} maxRows={50} />
        ) : (
          <div className="space-y-8">
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

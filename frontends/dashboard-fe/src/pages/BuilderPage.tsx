import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { reportApi } from '@api/reportApi'
import type { Report, ReportFilter } from '@shared/types/report'
import { ReportType } from '@shared/types/report'

interface ReportConfig {
  title: string
  description: string
  type: 'table' | 'chart' | 'summary'
  filters: Record<string, string>
}

const TYPE_MAP: Record<ReportConfig['type'], ReportType> = {
  table: ReportType.TABULAR,
  chart: ReportType.MATRIX,
  summary: ReportType.SUMMARY,
}

export const BuilderPage: React.FC = () => {
  const navigate = useNavigate()
  const [config, setConfig] = useState<ReportConfig>({
    title: '',
    description: '',
    type: 'table',
    filters: {}
  })
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSave = async () => {
    setError(null)
    const filters: ReportFilter[] = Object.entries(config.filters).map(([field, value]) => ({
      field,
      operator: 'eq',
      value,
    }))
    const report: Report = {
      id: '',
      name: config.title,
      description: config.description,
      report_type: TYPE_MAP[config.type],
      object_type: 'Case',
      fields: [],
      filters,
      aggregations: [],
      metadata: {
        created_by: 'user',
        created_at: new Date().toISOString(),
      },
    }
    try {
      await reportApi.createReport(report)
      setSaved(true)
      setTimeout(() => navigate('/'), 2000)
    } catch (err) {
      setError('Falha ao salvar o relatório. Tente novamente.')
    }
  }

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-4xl mx-auto bg-card border border-border rounded-lg p-8">
        <h1 className="text-2xl font-bold text-primary-dark mb-6">Criar Novo Relatório</h1>

        <div className="space-y-6">
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
              Título do Relatório
            </label>
            <input
              id="title"
              type="text"
              value={config.title}
              onChange={(e) => setConfig({ ...config, title: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
              placeholder="ex: Relatório de Vendas Q4"
            />
          </div>

          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
              Descrição
            </label>
            <textarea
              id="description"
              value={config.description}
              onChange={(e) => setConfig({ ...config, description: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-transparent"
              rows={4}
              placeholder="Descreva o propósito do relatório..."
            />
          </div>

          <fieldset>
            <legend className="block text-sm font-medium text-gray-700 mb-2">
              Tipo de Visualização
            </legend>
            <div className="grid grid-cols-3 gap-4">
              {(['table', 'chart', 'summary'] as const).map((type) => (
                <button
                  key={type}
                  type="button"
                  onClick={() => setConfig({ ...config, type })}
                  className={`p-4 rounded-md border-2 font-semibold capitalize transition-colors cursor-pointer ${
                    config.type === type
                      ? 'border-primary bg-primary text-white'
                      : 'border-gray-300 bg-card text-gray-700 hover:border-primary'
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>
          </fieldset>

          {error && (
            <p role="alert" className="text-sm text-destructive bg-red-50 border border-red-200 rounded-md p-2">
              {error}
            </p>
          )}

          <div className="flex gap-4 pt-6">
            <button
              onClick={handleSave}
              disabled={!config.title || saved}
              className="flex-1 bg-primary text-white font-semibold py-2.5 rounded-md hover:bg-primary-dark disabled:bg-gray-400 transition-colors cursor-pointer disabled:cursor-not-allowed"
            >
              {saved ? 'Relatório Criado!' : 'Salvar Relatório'}
            </button>
            <button
              onClick={() => navigate('/')}
              className="flex-1 bg-card border border-border text-gray-700 font-semibold py-2.5 rounded-md hover:bg-muted transition-colors cursor-pointer"
            >
              Cancelar
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
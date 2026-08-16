import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

interface ReportConfig {
  title: string
  description: string
  type: 'table' | 'chart' | 'summary'
  filters: Record<string, string>
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

  const handleSave = async () => {
    try {
      const response = await fetch('/api/reports', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(config)
      })

      if (response.ok) {
        setSaved(true)
        setTimeout(() => navigate('/'), 2000)
      }
    } catch (error) {
      console.error('Error saving report:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-xl p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Criar Novo Relatório</h1>

        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Título do Relatório
            </label>
            <input
              type="text"
              value={config.title}
              onChange={(e) => setConfig({ ...config, title: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="ex: Relatório de Vendas Q4"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Descrição
            </label>
            <textarea
              value={config.description}
              onChange={(e) => setConfig({ ...config, description: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              rows={4}
              placeholder="Descreva o propósito do relatório..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tipo de Visualização
            </label>
            <div className="grid grid-cols-3 gap-4">
              {(['table', 'chart', 'summary'] as const).map((type) => (
                <button
                  key={type}
                  onClick={() => setConfig({ ...config, type })}
                  className={`p-4 rounded-lg border-2 font-semibold capitalize transition-all ${
                    config.type === type
                      ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                      : 'border-gray-300 bg-white text-gray-700 hover:border-indigo-300'
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>
          </div>

          <div className="flex gap-4 pt-6">
            <button
              onClick={handleSave}
              disabled={!config.title || saved}
              className="flex-1 bg-indigo-600 text-white font-semibold py-3 rounded-lg hover:bg-indigo-700 disabled:bg-gray-400 transition-colors"
            >
              {saved ? '✓ Relatório Criado!' : 'Salvar Relatório'}
            </button>
            <button
              onClick={() => navigate('/')}
              className="flex-1 bg-gray-200 text-gray-700 font-semibold py-3 rounded-lg hover:bg-gray-300 transition-colors"
            >
              Cancelar
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

import React, { useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useReportFormStore } from '@stores/reportFormStore'
import { FormStep } from '@components/FormStep'
import { reportApi } from '@api/reportApi'
import { logger } from '@shared/utils/logger'

const STEPS = [
  { id: 1, title: 'Informações Básicas', subtitle: 'Nome, descrição e tipo' },
  { id: 2, title: 'Objeto e Campos', subtitle: 'Selecione o objeto e campos' },
  { id: 3, title: 'Filtros', subtitle: 'Adicione filtros ao relatório' },
  { id: 4, title: 'Agregações', subtitle: 'Configure agregações' },
  { id: 5, title: 'Agendamento', subtitle: 'Configure execução automática' },
  { id: 6, title: 'Revisão', subtitle: 'Revise e salve' },
]

export const BuilderPage: React.FC = () => {
  const { id } = useParams<{ id?: string }>()
  const navigate = useNavigate()
  const { report, step, errors, loading, dirty, setStep, initializeForm, setLoading } =
    useReportFormStore()

  useEffect(() => {
    if (id) {
      const loadReport = async () => {
        try {
          setLoading(true)
          const data = await reportApi.getReport(id)
          initializeForm(data)
          logger.info('Report loaded for editing', { report_id: id })
        } catch (error) {
          logger.error('Failed to load report', error instanceof Error ? error : new Error(String(error)))
          navigate('/dashboard')
        } finally {
          setLoading(false)
        }
      }
      loadReport()
    } else {
      initializeForm()
    }
  }, [id, initializeForm, setLoading, navigate])

  const handleStepClick = (stepId: number) => {
    if (stepId <= step || errors.length === 0) {
      setStep(stepId)
    }
  }

  const handleSave = async () => {
    try {
      setLoading(true)
      const result = id
        ? await reportApi.updateReport(id, report)
        : await reportApi.createReport(report)

      if (result.success) {
        logger.info('Report saved successfully', { report_id: result.report_id })
        navigate('/dashboard')
      }
    } catch (error) {
      logger.error('Failed to save report', error instanceof Error ? error : new Error(String(error)))
    } finally {
      setLoading(false)
    }
  }

  if (loading && id) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin">
          <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full" />
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-card border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                {id ? 'Editar' : 'Criar'} Relatório
              </h1>
              <p className="text-gray-600 mt-2">Passo {step} de {STEPS.length}</p>
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
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar with steps */}
          <aside className="lg:col-span-1">
            <div className="space-y-2">
              {STEPS.map((s) => (
                <FormStep
                  key={s.id}
                  step={s.id}
                  title={s.title}
                  subtitle={s.subtitle}
                  isActive={step === s.id}
                  isCompleted={step > s.id}
                  onClick={() => handleStepClick(s.id)}
                />
              ))}
            </div>
          </aside>

          {/* Main content */}
          <div className="lg:col-span-3">
            <div className="bg-card border border-border rounded-lg p-8">
              <div className="min-h-96">
                <p className="text-gray-500 text-center py-12">
                  Passo {step} em desenvolvimento...
                </p>
              </div>

              {/* Navigation buttons */}
              <div className="flex justify-between mt-8 pt-6 border-t border-gray-200">
                <button
                  onClick={() => setStep(Math.max(1, step - 1))}
                  disabled={step === 1}
                  className="px-6 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition"
                >
                  ← Anterior
                </button>

                <button
                  onClick={handleSave}
                  disabled={loading || !dirty}
                  className="px-6 py-2 bg-primary text-white rounded-md hover:bg-primary-dark disabled:bg-gray-400 disabled:cursor-not-allowed transition cursor-pointer"
                >
                  {loading ? 'Salvando...' : id ? 'Atualizar' : 'Criar'}
                </button>

                <button
                  onClick={() => setStep(Math.min(STEPS.length, step + 1))}
                  disabled={step === STEPS.length}
                  className="px-6 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition"
                >
                  Próximo →
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

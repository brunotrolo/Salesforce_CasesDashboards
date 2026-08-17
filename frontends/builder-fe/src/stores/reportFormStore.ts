import { create } from 'zustand'
import { Report, ReportType, ReportStatus } from '@typings/report'
import { FormState, ValidationMessage } from '@typings/form'

interface ReportFormStore extends FormState {
  setStep: (step: number) => void
  updateReport: (updates: Partial<Report>) => void
  setErrors: (errors: ValidationMessage[]) => void
  addError: (error: ValidationMessage) => void
  clearErrors: () => void
  setLoading: (loading: boolean) => void
  setSaved: (saved: boolean) => void
  setDirty: (dirty: boolean) => void
  resetForm: () => void
  initializeForm: (report?: Report) => void
}

const createDefaultReport = (): Report => ({
  id: `report:${Date.now()}`,
  name: '',
  description: '',
  report_type: ReportType.SUMMARY,
  object_type: 'Case',
  fields: [],
  filters: [],
  aggregations: [],
  schedule: {
    enabled: false,
    max_rows: 10000,
  },
  metadata: {
    created_by: 'current-user',
    created_at: new Date().toISOString(),
  },
  status: ReportStatus.DRAFT,
  limit: 10000,
})

export const useReportFormStore = create<ReportFormStore>((set) => ({
  report: createDefaultReport(),
  step: 1,
  errors: [],
  loading: false,
  saved: false,
  dirty: false,

  setStep: (step) => set({ step }),

  updateReport: (updates) =>
    set((state) => ({
      report: { ...state.report, ...updates },
      dirty: true,
    })),

  setErrors: (errors) => set({ errors }),

  addError: (error) =>
    set((state) => ({
      errors: [...state.errors, error],
    })),

  clearErrors: () => set({ errors: [] }),

  setLoading: (loading) => set({ loading }),

  setSaved: (saved) => set({ saved }),

  setDirty: (dirty) => set({ dirty }),

  resetForm: () =>
    set({
      report: createDefaultReport(),
      step: 1,
      errors: [],
      loading: false,
      saved: false,
      dirty: false,
    }),

  initializeForm: (report) => {
    if (report) {
      set({
        report,
        step: 1,
        errors: [],
        loading: false,
        saved: true,
        dirty: false,
      })
    } else {
      set({
        report: createDefaultReport(),
        step: 1,
        errors: [],
        loading: false,
        saved: false,
        dirty: false,
      })
    }
  },
}))

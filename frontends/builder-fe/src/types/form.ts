import { Report } from '@shared/types/report'

export interface FormStep {
  id: number
  title: string
  completed: boolean
}

export interface SalesforceObject {
  name: string
  label: string
  fields: SalesforceField[]
}

export interface SalesforceField {
  name: string
  label: string
  type: string
  required: boolean
  referenceTo?: string[]
}

export interface ValidationMessage {
  field: string
  message: string
  code: string
  severity: 'error' | 'warning'
}

export interface FormState {
  report: Report
  step: number
  errors: ValidationMessage[]
  loading: boolean
  saved: boolean
  dirty: boolean
}

export interface FilterDraft {
  id: string
  field: string
  operator: string
  value: string | number | null
  error?: string
}

export interface AggregationDraft {
  id: string
  field: string
  function: string
  label: string
  error?: string
}

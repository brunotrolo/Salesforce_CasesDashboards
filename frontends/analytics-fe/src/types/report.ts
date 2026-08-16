export enum ReportStatus {
  DRAFT = 'DRAFT',
  ACTIVE = 'ACTIVE',
  SCHEDULED = 'SCHEDULED',
  PAUSED = 'PAUSED',
  ARCHIVED = 'ARCHIVED',
}

export enum ReportType {
  SUMMARY = 'SUMMARY',
  MATRIX = 'MATRIX',
  TABULAR = 'TABULAR',
  JOIN = 'JOIN',
}

export interface ReportFilter {
  field: string
  operator: 'eq' | 'ne' | 'gt' | 'lt' | 'gte' | 'lte' | 'in' | 'contains' | 'startswith' | 'endswith' | 'between' | 'is_null'
  value: string | number | null
}

export interface ReportAggregation {
  field: string
  function: 'sum' | 'avg' | 'count' | 'min' | 'max' | 'count_distinct'
  label?: string
}

export interface ReportSchedule {
  enabled: boolean
  cron?: string
  max_rows?: number
}

export interface ReportMetadata {
  created_by: string
  created_at: string
  updated_by?: string
  updated_at?: string
  version?: string
}

export interface Report {
  id: string
  name: string
  description?: string
  report_type: ReportType
  object_type: string
  fields: string[]
  filters?: ReportFilter[]
  aggregations?: ReportAggregation[]
  schedule?: ReportSchedule
  metadata: ReportMetadata
  status?: ReportStatus
  limit?: number
}

export interface ReportExecutionResult {
  report_id: string
  status: 'success' | 'failed' | 'pending'
  rows_returned: number
  execution_time_ms: number
  executed_at: string
  data: Record<string, any>[]
  error?: string
  warning?: string
}

export interface ListReportsResponse {
  success: boolean
  total: number
  items: Report[]
  offset: number
  limit: number
}

export interface CreateReportResponse {
  success: boolean
  report_id: string
  status: ReportStatus
  validation_errors?: Array<{
    field: string
    message: string
    code: string
  }>
}

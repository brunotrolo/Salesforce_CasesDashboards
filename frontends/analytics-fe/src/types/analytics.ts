export interface ChartData {
  name: string
  value: number
  label?: string
}

export interface AnalyticsResult {
  report_id: string
  report_name: string
  executed_at: string
  execution_time_ms: number
  rows_returned: number
  data: Record<string, any>[]
  aggregations?: AggregationResult[]
}

export interface AggregationResult {
  field: string
  function: string
  label: string
  value: number | string
}

export interface ChartConfig {
  type: 'line' | 'bar' | 'pie' | 'area' | 'scatter'
  title: string
  xAxis?: string
  yAxis?: string
  color?: string
}

export interface TableColumn {
  key: string
  label: string
  type: 'string' | 'number' | 'date' | 'currency'
}

export interface TableData {
  columns: TableColumn[]
  rows: Record<string, any>[]
  total: number
}

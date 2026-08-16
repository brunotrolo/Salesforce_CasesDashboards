import { useState, useCallback } from 'react'
import { Report, ReportStatus, ListReportsResponse } from '@types/report'
import { reportApi } from '@api/reportApi'

export interface UseReportsState {
  reports: Report[]
  loading: boolean
  error: string | null
  total: number
  offset: number
  limit: number
}

export function useReports() {
  const [state, setState] = useState<UseReportsState>({
    reports: [],
    loading: false,
    error: null,
    total: 0,
    offset: 0,
    limit: 10,
  })

  const loadReports = useCallback(async (status?: ReportStatus) => {
    setState((prev) => ({ ...prev, loading: true, error: null }))
    try {
      const result = await reportApi.listReports(state.limit, state.offset, status)
      setState((prev) => ({
        ...prev,
        reports: result.items,
        total: result.total,
        loading: false,
      }))
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to load reports'
      setState((prev) => ({ ...prev, error: message, loading: false }))
    }
  }, [state.limit, state.offset])

  const getReport = useCallback(async (reportId: string) => {
    setState((prev) => ({ ...prev, loading: true, error: null }))
    try {
      const report = await reportApi.getReport(reportId)
      return report
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to load report'
      setState((prev) => ({ ...prev, error: message, loading: false }))
      throw error
    }
  }, [])

  const executeReport = useCallback(async (reportId: string) => {
    setState((prev) => ({ ...prev, loading: true, error: null }))
    try {
      const result = await reportApi.executeReport(reportId)
      setState((prev) => ({ ...prev, loading: false }))
      return result
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to execute report'
      setState((prev) => ({ ...prev, error: message, loading: false }))
      throw error
    }
  }, [])

  const deleteReport = useCallback(async (reportId: string) => {
    setState((prev) => ({ ...prev, loading: true, error: null }))
    try {
      await reportApi.deleteReport(reportId)
      setState((prev) => ({
        ...prev,
        reports: prev.reports.filter((r) => r.id !== reportId),
        loading: false,
      }))
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to delete report'
      setState((prev) => ({ ...prev, error: message, loading: false }))
      throw error
    }
  }, [])

  const setPagination = useCallback((offset: number, limit: number) => {
    setState((prev) => ({ ...prev, offset, limit }))
  }, [])

  return {
    ...state,
    loadReports,
    getReport,
    executeReport,
    deleteReport,
    setPagination,
  }
}

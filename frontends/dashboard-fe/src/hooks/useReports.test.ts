import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { useReports } from './useReports'
import * as reportApi from '../api/reportApi'
import type { Report, ReportStatus, ReportType } from '../types/report'

vi.mock('@api/reportApi')

const mockReports: Report[] = [
  {
    id: 'report:1',
    name: 'Report 1',
    report_type: ReportType.SUMMARY,
    object_type: 'Case',
    fields: ['Id', 'Status'],
    metadata: {
      created_by: 'u:123',
      created_at: new Date().toISOString(),
    },
    status: ReportStatus.ACTIVE,
  },
]

describe('useReports', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('initializes with default state', () => {
    const { result } = renderHook(() => useReports())

    expect(result.current.reports).toEqual([])
    expect(result.current.loading).toBe(false)
    expect(result.current.error).toBeNull()
    expect(result.current.total).toBe(0)
  })

  it('loads reports successfully', async () => {
    const mockResponse = {
      items: mockReports,
      total: 1,
      offset: 0,
      limit: 10,
      success: true,
    }

    vi.spyOn(reportApi.reportApi, 'listReports').mockResolvedValue(mockResponse)

    const { result } = renderHook(() => useReports())

    act(() => {
      result.current.loadReports()
    })

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.reports).toEqual(mockReports)
    expect(result.current.total).toBe(1)
    expect(result.current.error).toBeNull()
  })

  it('handles load error', async () => {
    const error = new Error('API Error')
    vi.spyOn(reportApi.reportApi, 'listReports').mockRejectedValue(error)

    const { result } = renderHook(() => useReports())

    act(() => {
      result.current.loadReports()
    })

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.error).toBe('API Error')
    expect(result.current.reports).toEqual([])
  })

  it('executes report successfully', async () => {
    const mockResult = {
      report_id: 'report:1',
      status: 'success',
      rows_returned: 10,
      execution_time_ms: 150,
      executed_at: new Date().toISOString(),
      data: [{ id: '1' }],
    }

    vi.spyOn(reportApi.reportApi, 'executeReport').mockResolvedValue(mockResult)

    const { result } = renderHook(() => useReports())

    let response
    await act(async () => {
      response = await result.current.executeReport('report:1')
    })

    expect(response).toEqual(mockResult)
    expect(reportApi.reportApi.executeReport).toHaveBeenCalledWith('report:1')
  })

  it('deletes report successfully', async () => {
    const mockResponse = { success: true }
    vi.spyOn(reportApi.reportApi, 'deleteReport').mockResolvedValue(mockResponse)

    const { result } = renderHook(() => useReports())

    // Pre-populate reports
    act(() => {
      result.current.reports.push(mockReports[0])
    })

    await act(async () => {
      await result.current.deleteReport('report:1')
    })

    expect(result.current.reports).toHaveLength(0)
  })

  it('updates pagination', () => {
    const { result } = renderHook(() => useReports())

    act(() => {
      result.current.setPagination(20, 10)
    })

    expect(result.current.offset).toBe(20)
    expect(result.current.limit).toBe(10)
  })
})

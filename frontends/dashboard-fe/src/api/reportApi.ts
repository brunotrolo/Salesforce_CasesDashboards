import axios from 'axios'
import type { Report, ReportExecutionResult, ListReportsResponse, CreateReportResponse, ReportStatus } from '../types/report'

const API_BASE = '/api'

const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const isLoginRequest = error.config?.url?.includes('/auth/login')
    if (error.response?.status === 401 && !isLoginRequest) {
      localStorage.removeItem('auth_token')
      window.location.href = '/'
    }
    return Promise.reject(error)
  }
)

export const reportApi = {
  async login(username: string, password: string): Promise<{ access_token: string; token_type: string }> {
    const response = await apiClient.post('/auth/login', { username, password })
    return response.data
  },

  async listReports(
    limit: number = 10,
    offset: number = 0,
    status?: ReportStatus
  ): Promise<ListReportsResponse> {
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString(),
    })
    if (status) {
      params.append('status', status)
    }
    const response = await apiClient.get(`/reports?${params}`)
    return response.data
  },

  async getReport(reportId: string): Promise<Report> {
    const response = await apiClient.get(`/reports/${reportId}`)
    return response.data
  },

  async createReport(report: Report): Promise<CreateReportResponse> {
    const response = await apiClient.post('/reports', report)
    return response.data
  },

  async updateReport(reportId: string, updates: Partial<Report>): Promise<CreateReportResponse> {
    const response = await apiClient.put(`/reports/${reportId}`, updates)
    return response.data
  },

  async deleteReport(reportId: string): Promise<{ success: boolean }> {
    const response = await apiClient.delete(`/reports/${reportId}`)
    return response.data
  },

  async executeReport(reportId: string): Promise<ReportExecutionResult> {
    const response = await apiClient.post(`/reports/${reportId}/execute`)
    return response.data
  },

  async activateReport(reportId: string): Promise<{ success: boolean }> {
    const response = await apiClient.post(`/reports/${reportId}/activate`)
    return response.data
  },

  async scheduleReport(reportId: string, cron: string): Promise<{ success: boolean }> {
    const response = await apiClient.post(`/reports/${reportId}/schedule`, { cron })
    return response.data
  },

  async pauseReport(reportId: string): Promise<{ success: boolean }> {
    const response = await apiClient.post(`/reports/${reportId}/pause`)
    return response.data
  },

  async validateReport(report: Report): Promise<{
    is_valid: boolean
    errors: Array<{ field: string; message: string; code: string }>
  }> {
    const response = await apiClient.post('/reports/validate', report)
    return response.data
  },
}

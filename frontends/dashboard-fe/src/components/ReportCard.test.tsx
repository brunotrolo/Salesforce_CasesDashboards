import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ReportCard } from './ReportCard'
import { Report, ReportStatus, ReportType } from '@types/report'

const mockReport: Report = {
  id: 'report:123',
  name: 'Test Report',
  description: 'A test report',
  report_type: ReportType.SUMMARY,
  object_type: 'Case',
  fields: ['Id', 'Status'],
  metadata: {
    created_by: 'u:123',
    created_at: new Date().toISOString(),
  },
  status: ReportStatus.ACTIVE,
}

describe('ReportCard', () => {
  it('renders report information', () => {
    const mocks = {
      onExecute: vi.fn(),
      onEdit: vi.fn(),
      onDelete: vi.fn(),
    }

    render(
      <ReportCard
        report={mockReport}
        {...mocks}
      />
    )

    expect(screen.getByText('Test Report')).toBeInTheDocument()
    expect(screen.getByText('A test report')).toBeInTheDocument()
    expect(screen.getByText('Case')).toBeInTheDocument()
  })

  it('displays correct status badge', () => {
    const mocks = {
      onExecute: vi.fn(),
      onEdit: vi.fn(),
      onDelete: vi.fn(),
    }

    render(
      <ReportCard
        report={mockReport}
        {...mocks}
      />
    )

    expect(screen.getByText('Ativo')).toBeInTheDocument()
  })

  it('calls onExecute when execute button is clicked', async () => {
    const user = userEvent.setup()
    const onExecute = vi.fn()
    const mocks = {
      onExecute,
      onEdit: vi.fn(),
      onDelete: vi.fn(),
    }

    render(
      <ReportCard
        report={mockReport}
        {...mocks}
      />
    )

    const executeBtn = screen.getByText('Executar')
    await user.click(executeBtn)

    expect(onExecute).toHaveBeenCalledWith(mockReport.id)
  })

  it('disables buttons when loading', () => {
    const mocks = {
      onExecute: vi.fn(),
      onEdit: vi.fn(),
      onDelete: vi.fn(),
    }

    render(
      <ReportCard
        report={mockReport}
        {...mocks}
        loading={true}
      />
    )

    const executeBtn = screen.getByText('Executar')
    const editBtn = screen.getByText('Editar')
    const deleteBtn = screen.getByText('Deletar')

    expect(executeBtn).toBeDisabled()
    expect(editBtn).toBeDisabled()
    expect(deleteBtn).toBeDisabled()
  })

  it('disables execute button for draft reports', () => {
    const draftReport = { ...mockReport, status: ReportStatus.DRAFT }
    const mocks = {
      onExecute: vi.fn(),
      onEdit: vi.fn(),
      onDelete: vi.fn(),
    }

    render(
      <ReportCard
        report={draftReport}
        {...mocks}
      />
    )

    const executeBtn = screen.getByText('Executar')
    expect(executeBtn).toBeDisabled()
  })
})

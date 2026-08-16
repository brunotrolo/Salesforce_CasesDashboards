/**
 * Tests for useReports hook
 * Tests report CRUD operations, loading states, and error handling
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import axios from 'axios';
import { useReports } from './useReports';

vi.mock('axios');
const mockedAxios = vi.mocked(axios);

describe('useReports', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should initialize with default state', () => {
    const { result } = renderHook(() => useReports());

    expect(result.current.reports).toEqual([]);
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('should load reports on mount', async () => {
    const mockReports = [
      { id: 'r1', name: 'Report 1', status: 'active', created_at: '2026-01-01' },
      { id: 'r2', name: 'Report 2', status: 'draft', created_at: '2026-01-02' }
    ];

    mockedAxios.get.mockResolvedValueOnce({ data: mockReports });

    const { result } = renderHook(() => useReports());

    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.reports).toEqual(mockReports);
    expect(mockedAxios.get).toHaveBeenCalledWith('/api/reports');
  });

  it('should handle load error', async () => {
    const error = new Error('Network error');
    mockedAxios.get.mockRejectedValueOnce(error);

    const { result } = renderHook(() => useReports());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.error).not.toBeNull();
    expect(result.current.reports).toEqual([]);
  });

  it('should get single report', async () => {
    const mockReport = {
      id: 'r1',
      name: 'Report 1',
      status: 'active',
      fields: ['Id', 'Name'],
      created_at: '2026-01-01'
    };

    mockedAxios.get.mockResolvedValueOnce({ data: mockReport });

    const { result } = renderHook(() => useReports());
    const report = await result.current.getReport('r1');

    expect(report).toEqual(mockReport);
    expect(mockedAxios.get).toHaveBeenCalledWith('/api/reports/r1');
  });

  it('should execute report', async () => {
    const mockResult = {
      execution_id: 'e1',
      status: 'success',
      rows: 100,
      results: []
    };

    mockedAxios.post.mockResolvedValueOnce({ data: mockResult });

    const { result } = renderHook(() => useReports());
    const execResult = await result.current.executeReport('r1');

    expect(execResult).toEqual(mockResult);
    expect(mockedAxios.post).toHaveBeenCalledWith('/api/reports/r1/execute');
  });

  it('should delete report', async () => {
    mockedAxios.delete.mockResolvedValueOnce({ data: { success: true } });

    const { result } = renderHook(() => useReports());
    await result.current.deleteReport('r1');

    expect(mockedAxios.delete).toHaveBeenCalledWith('/api/reports/r1');
  });
});

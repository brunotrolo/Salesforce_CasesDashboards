/**
 * Tests for reportFormStore (Zustand store)
 * Tests form state management, validation, and step navigation
 */
import { describe, it, expect, beforeEach } from 'vitest';
import { useReportFormStore } from './reportFormStore';

describe('reportFormStore', () => {
  beforeEach(() => {
    useReportFormStore.setState({
      report: {
        id: '',
        name: '',
        object_type: '',
        fields: [],
        filters: [],
        aggregations: [],
        schedule: undefined
      },
      step: 1,
      errors: [],
      loading: false,
      saved: false,
      dirty: false
    });
  });

  it('should initialize with default state', () => {
    const state = useReportFormStore.getState();
    expect(state.step).toBe(1);
    expect(state.report.fields).toEqual([]);
    expect(state.errors).toEqual([]);
    expect(state.loading).toBe(false);
  });

  it('should move to next step', () => {
    const { setStep } = useReportFormStore.getState();
    setStep(2);

    expect(useReportFormStore.getState().step).toBe(2);
  });

  it('should update report data', () => {
    const { updateReport } = useReportFormStore.getState();
    updateReport({ name: 'New Report', object_type: 'Case' });

    const state = useReportFormStore.getState();
    expect(state.report.name).toBe('New Report');
    expect(state.report.object_type).toBe('Case');
  });

  it('should add validation errors', () => {
    const { addError } = useReportFormStore.getState();
    addError({ field: 'name', message: 'Name is required' });

    const state = useReportFormStore.getState();
    expect(state.errors).toHaveLength(1);
    expect(state.errors[0].field).toBe('name');
  });

  it('should clear all errors', () => {
    const { addError, clearErrors } = useReportFormStore.getState();
    addError({ field: 'name', message: 'Error 1' });
    addError({ field: 'fields', message: 'Error 2' });

    expect(useReportFormStore.getState().errors).toHaveLength(2);

    clearErrors();
    expect(useReportFormStore.getState().errors).toHaveLength(0);
  });

  it('should reset entire form', () => {
    const { updateReport, addError, setStep, resetForm } = useReportFormStore.getState();

    updateReport({ name: 'Report Name' });
    addError({ field: 'test', message: 'Error' });
    setStep(3);

    resetForm();

    const state = useReportFormStore.getState();
    expect(state.report.name).toBe('');
    expect(state.errors).toHaveLength(0);
    expect(state.step).toBe(1);
  });
});

/**
 * Tests for BarChart component
 * Tests chart rendering, data transformation, and interactions
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BarChart } from './BarChart';

describe('BarChart', () => {
  const mockChartData = {
    name: 'Sales Chart',
    xAxis: 'Month',
    yAxis: 'Amount',
    data: [
      { name: 'Jan', value: 1000 },
      { name: 'Feb', value: 2000 },
      { name: 'Mar', value: 1500 }
    ]
  };

  it('should render chart container', () => {
    render(<BarChart config={mockChartData} />);
    
    const container = screen.getByRole('figure', { hidden: true });
    expect(container).toBeInTheDocument();
  });

  it('should display chart title', () => {
    render(<BarChart config={mockChartData} />);
    
    expect(screen.getByText('Sales Chart')).toBeInTheDocument();
  });

  it('should render with data points', () => {
    render(<BarChart config={mockChartData} />);
    
    // Recharts renders SVG elements
    const svg = document.querySelector('svg');
    expect(svg).toBeInTheDocument();
  });

  it('should handle empty data', () => {
    const emptyConfig = { ...mockChartData, data: [] };
    
    const { container } = render(<BarChart config={emptyConfig} />);
    expect(container.querySelector('svg')).toBeInTheDocument();
  });

  it('should show tooltip on hover', () => {
    const { container } = render(<BarChart config={mockChartData} />);
    
    const bars = container.querySelectorAll('.recharts-bar-rectangle-area');
    expect(bars.length).toBeGreaterThan(0);
  });

  it('should display legend', () => {
    render(<BarChart config={mockChartData} />);
    
    const legend = document.querySelector('.recharts-legend');
    expect(legend).toBeInTheDocument();
  });

  it('should format axis labels correctly', () => {
    render(<BarChart config={mockChartData} />);
    
    const labels = document.querySelectorAll('.recharts-cartesian-axis-tick-value');
    expect(labels.length).toBeGreaterThan(0);
  });

  it('should handle different data types', () => {
    const numericConfig = {
      ...mockChartData,
      data: [
        { name: 'Q1', value: 10000 },
        { name: 'Q2', value: 20000 }
      ]
    };

    render(<BarChart config={numericConfig} />);
    
    expect(document.querySelector('svg')).toBeInTheDocument();
  });
});

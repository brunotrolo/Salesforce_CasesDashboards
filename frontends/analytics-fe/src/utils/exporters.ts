/**
 * Export utilities for reports (PDF, Excel)
 */
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import * as XLSX from 'xlsx';
import { toPng } from 'html-to-image';
import { AnalyticsResult } from '../types/analytics';

/**
 * Export report to PDF with charts and data
 */
export async function exportToPDF(
  reportName: string,
  results: AnalyticsResult,
  chartElement?: HTMLElement
): Promise<void> {
  const pdf = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: 'a4'
  });

  // Add title
  pdf.setFontSize(16);
  pdf.text(reportName, 20, 20);

  // Add summary statistics
  pdf.setFontSize(10);
  let yPosition = 35;

  pdf.text(`Total Rows: ${results.rows_returned}`, 20, yPosition);
  yPosition += 8;
  pdf.text(`Execution Time: ${results.execution_time_ms}ms`, 20, yPosition);
  yPosition += 15;

  // Add chart if available
  if (chartElement) {
    try {
      const imageData = await toPng(chartElement);
      const imgDimensions = pdf.getImageProperties(imageData);
      const imgWidth = 170;
      const imgHeight = (imgDimensions.height * imgWidth) / imgDimensions.width;

      pdf.addImage(imageData, 'PNG', 20, yPosition, imgWidth, imgHeight);
      yPosition += imgHeight + 15;
    } catch (error) {
      console.error('Error capturing chart:', error);
    }
  }

  // Add data table
  if (results.data && results.data.length > 0) {
    pdf.setFontSize(12);
    pdf.text('Data Table', 20, yPosition);
    yPosition += 10;

    const columns = Object.keys(results.data[0]);
    const rows = results.data.slice(0, 20).map(row =>
      columns.map(col => String(row[col] || ''))
    );

    autoTable(pdf, {
      head: [columns],
      body: rows,
      startY: yPosition,
      margin: { top: 20, right: 20, bottom: 20, left: 20 }
    });
  }

  // Add footer
  const pageCount = pdf.getNumberOfPages();
  for (let i = 1; i <= pageCount; i++) {
    pdf.setPage(i);
    pdf.setFontSize(8);
    pdf.text(
      `Page ${i} of ${pageCount}`,
      pdf.internal.pageSize.getWidth() / 2,
      pdf.internal.pageSize.getHeight() - 10,
      { align: 'center' }
    );
  }

  pdf.save(`${reportName}-${new Date().toISOString().split('T')[0]}.pdf`);
}

/**
 * Export report data to Excel
 */
export function exportToExcel(
  reportName: string,
  results: AnalyticsResult,
  summary?: Record<string, any>
): void {
  const workbook = XLSX.utils.book_new();

  // Summary sheet
  if (summary) {
    const summaryData = [
      ['Report Name', reportName],
      ['Execution Date', new Date().toISOString()],
      ['Total Rows', results.rows_returned],
      ['Execution Time (ms)', results.execution_time_ms]
    ];

    const summarySheet = XLSX.utils.aoa_to_sheet(summaryData);
    XLSX.utils.book_append_sheet(workbook, summarySheet, 'Summary');
  }

  // Data sheet
  if (results.data && results.data.length > 0) {
    const dataSheet = XLSX.utils.json_to_sheet(results.data);

    // Auto-fit column widths
    const maxWidth = 50;
    const colWidths = Object.keys(results.data[0]).map(col => ({
      wch: Math.min(
        Math.max(...results.data.map(row => String(row[col] || '').length)) + 2,
        maxWidth
      )
    }));
    dataSheet['!cols'] = colWidths;

    XLSX.utils.book_append_sheet(workbook, dataSheet, 'Data');
  }

  XLSX.writeFile(workbook, `${reportName}-${new Date().toISOString().split('T')[0]}.xlsx`);
}

/**
 * Export as CSV
 */
export function exportToCSV(
  reportName: string,
  data: Record<string, any>[]
): void {
  const csv = XLSX.utils.json_to_sheet(data);
  const csvContent = XLSX.utils.sheet_to_csv(csv);

  const blob = new Blob([csvContent], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');

  link.href = url;
  link.download = `${reportName}-${new Date().toISOString().split('T')[0]}.csv`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}

/**
 * Copy data to clipboard
 */
export async function copyToClipboard(data: Record<string, any>[]): Promise<void> {
  const csv = data
    .map(row => Object.values(row).join('\t'))
    .join('\n');

  try {
    await navigator.clipboard.writeText(csv);
    console.log('Data copied to clipboard');
  } catch (error) {
    console.error('Failed to copy to clipboard:', error);
  }
}

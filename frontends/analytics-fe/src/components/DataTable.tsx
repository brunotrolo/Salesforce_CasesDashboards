import React from 'react'
import { TableData } from '@typings/analytics'
import { formatNumber, formatCurrency, formatDate } from '@utils/formatters'

interface DataTableProps {
  data: TableData
  maxRows?: number
}

export const DataTable: React.FC<DataTableProps> = ({ data, maxRows = 10 }) => {
  const displayRows = data.rows.slice(0, maxRows)

  const formatValue = (value: any, type: string) => {
    if (value === null || value === undefined) return '-'

    switch (type) {
      case 'number':
        return formatNumber(Number(value))
      case 'currency':
        return formatCurrency(Number(value))
      case 'date':
        return formatDate(value)
      default:
        return String(value)
    }
  }

  return (
    <div className="bg-card border border-border rounded-lg overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-sm text-gray-700">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              {data.columns.map((col) => (
                <th key={col.key} className="px-6 py-3 text-left font-semibold text-gray-900">
                  {col.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {displayRows.map((row, idx) => (
              <tr key={idx} className="border-b border-gray-200 hover:bg-gray-50 transition">
                {data.columns.map((col) => (
                  <td key={col.key} className="px-6 py-3">
                    {formatValue(row[col.key], col.type)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {data.rows.length > maxRows && (
        <div className="bg-gray-50 px-6 py-4 border-t border-gray-200">
          <p className="text-sm text-gray-600">
            Exibindo {displayRows.length} de {data.rows.length} linhas
          </p>
        </div>
      )}
    </div>
  )
}

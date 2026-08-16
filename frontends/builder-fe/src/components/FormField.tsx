import React from 'react'

interface FormFieldProps {
  label: string
  required?: boolean
  error?: string
  help?: string
  children: React.ReactNode
}

export const FormField: React.FC<FormFieldProps> = ({
  label,
  required = false,
  error,
  help,
  children,
}) => {
  return (
    <div className="mb-6">
      <label className="block text-sm font-semibold text-gray-900 mb-2">
        {label}
        {required && <span className="text-red-600 ml-1">*</span>}
      </label>
      <div className="relative">
        {children}
      </div>
      {error && (
        <p className="text-red-600 text-sm mt-2">{error}</p>
      )}
      {help && !error && (
        <p className="text-gray-500 text-sm mt-2">{help}</p>
      )}
    </div>
  )
}

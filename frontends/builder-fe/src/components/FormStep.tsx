import React from 'react'

interface FormStepProps {
  step: number
  title: string
  subtitle?: string
  isActive: boolean
  isCompleted: boolean
  onClick: () => void
}

export const FormStep: React.FC<FormStepProps> = ({
  step,
  title,
  subtitle,
  isActive,
  isCompleted,
  onClick,
}) => {
  return (
    <button
      onClick={onClick}
      disabled={!isActive && !isCompleted}
      className={`flex items-start gap-4 p-4 rounded-lg transition ${
        isActive
          ? 'bg-primary border-2 border-primary'
          : isCompleted
          ? 'bg-green-50 border-2 border-green-500 opacity-70 hover:opacity-100 cursor-pointer'
          : 'bg-gray-50 border-2 border-gray-200 opacity-50 cursor-not-allowed'
      }`}
    >
      <div
        className={`flex items-center justify-center w-8 h-8 rounded-full font-bold text-sm ${
          isActive
            ? 'bg-primary text-white'
            : isCompleted
            ? 'bg-green-500 text-white'
            : 'bg-gray-300 text-gray-600'
        }`}
      >
        {isCompleted ? '✓' : step}
      </div>
      <div className="text-left">
        <h3 className="font-semibold text-gray-900">{title}</h3>
        {subtitle && <p className="text-sm text-gray-600 mt-1">{subtitle}</p>}
      </div>
    </button>
  )
}

import { InputHTMLAttributes } from 'react'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
}

export function Input({ label, error, className = '', id, ...props }: InputProps) {
  const inputId = id || label?.toLowerCase().replace(/\s+/g, '-')
  return (
    <div className="flex flex-col gap-1">
      {label && (
        <label htmlFor={inputId} className="text-sm font-medium text-navy">
          {label}
        </label>
      )}
      <input
        id={inputId}
        className={`min-h-[44px] rounded-brand border border-mist bg-white px-3 py-2 text-sm text-navy outline-none focus:border-teal ${className}`}
        {...props}
      />
      {error && <span className="text-xs text-alert">{error}</span>}
    </div>
  )
}

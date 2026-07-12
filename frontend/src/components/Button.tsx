import { ButtonHTMLAttributes, ReactNode } from 'react'

type Variant = 'primary' | 'secondary' | 'ghost' | 'danger'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  children: ReactNode
}

const variants: Record<Variant, string> = {
  primary: 'bg-amber text-navy font-bold hover:opacity-90',
  secondary: 'bg-deep-blue text-white hover:opacity-90',
  ghost: 'bg-transparent text-teal border border-mist hover:bg-mist/50',
  danger: 'bg-alert text-white hover:opacity-90',
}

export function Button({ variant = 'primary', className = '', children, ...props }: ButtonProps) {
  return (
    <button
      className={`inline-flex min-h-[44px] items-center justify-center rounded-brand px-4 py-2 text-sm font-medium transition ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  )
}

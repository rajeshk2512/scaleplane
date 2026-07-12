import { ReactNode } from 'react'

export function Card({ children, className = '' }: { children: ReactNode; className?: string }) {
  return (
    <div className={`rounded-brand border border-mist bg-white p-6 shadow-sm ${className}`}>
      {children}
    </div>
  )
}

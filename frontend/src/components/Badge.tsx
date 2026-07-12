import { ReactNode } from 'react'

export function Badge({ children, variant = 'default' }: { children: ReactNode; variant?: 'default' | 'teal' | 'amber' }) {
  const styles = {
    default: 'bg-mist text-slate',
    teal: 'bg-teal/10 text-teal',
    amber: 'bg-amber/15 text-navy',
  }
  return (
    <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${styles[variant]}`}>
      {children}
    </span>
  )
}

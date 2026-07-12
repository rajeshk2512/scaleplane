import { ReactNode } from 'react'
import { NavBar } from './NavBar'

export function AppLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-cloud">
      <NavBar />
      <main className="mx-auto max-w-6xl px-6 py-8">{children}</main>
    </div>
  )
}

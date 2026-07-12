import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { Button } from './Button'

const navItems = [
  { to: '/', label: 'Dashboard' },
  { to: '/projects', label: 'Projects' },
  { to: '/members', label: 'Members' },
  { to: '/providers', label: 'Providers' },
  { to: '/settings', label: 'Settings' },
]

export function NavBar() {
  const { user, logout } = useAuth()
  const location = useLocation()

  return (
    <header className="border-b border-mist bg-deep-blue text-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <div className="flex items-center gap-8">
          <Link to="/" className="flex items-center gap-3">
            <img src="/logo.svg" alt="ScalePlane" className="h-8 w-8" />
            <span className="font-display text-lg font-bold">ScalePlane</span>
          </Link>
          <nav className="hidden gap-1 md:flex">
            {navItems.map((item) => (
              <Link
                key={item.to}
                to={item.to}
                className={`rounded-brand px-3 py-2 text-sm font-medium transition ${
                  location.pathname === item.to || (item.to !== '/' && location.pathname.startsWith(item.to))
                    ? 'bg-white/15 text-white'
                    : 'text-white/80 hover:bg-white/10 hover:text-white'
                }`}
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </div>
        <div className="flex items-center gap-4">
          <span className="hidden text-sm text-white/80 sm:inline">{user?.email}</span>
          <Button variant="ghost" onClick={logout} className="!min-h-0 !border-white/30 !text-white">
            Sign out
          </Button>
        </div>
      </div>
    </header>
  )
}

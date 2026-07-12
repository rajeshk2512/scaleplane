import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { api, clearTokens, setTokens, User } from '../api/client'

interface AuthState {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, fullName?: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthState | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      setLoading(false)
      return
    }
    api.me()
      .then(setUser)
      .catch(() => clearTokens())
      .finally(() => setLoading(false))
  }, [])

  const login = async (email: string, password: string) => {
    const tokens = await api.login(email, password)
    setTokens(tokens.access_token, tokens.refresh_token)
    const me = await api.me()
    setUser(me)
  }

  const register = async (email: string, password: string, fullName?: string) => {
    await api.register(email, password, fullName)
    await login(email, password)
  }

  const logout = () => {
    clearTokens()
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}

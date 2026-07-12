import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { api, clearTokens, getOrganizationId, setTokens, User } from '../api/client'

interface AuthState {
  user: User | null
  organizationId: string | null
  hasOrganization: boolean
  loading: boolean
  login: (email: string, password: string) => Promise<string | null>
  register: (email: string, password: string, fullName?: string) => Promise<string | null>
  logout: () => void
  switchOrganization: (organizationId: string) => Promise<void>
  setOrganizationFromTokens: (access: string, refresh: string, organizationId?: string | null) => void
}

const AuthContext = createContext<AuthState | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient()
  const [user, setUser] = useState<User | null>(null)
  const [organizationId, setOrganizationId] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  const applyTokens = (access: string, refresh: string, orgId?: string | null) => {
    setTokens(access, refresh, orgId)
    setOrganizationId(orgId ?? null)
  }

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      setLoading(false)
      return
    }
    setOrganizationId(getOrganizationId())
    api.me()
      .then(setUser)
      .catch(() => {
        clearTokens()
        setOrganizationId(null)
      })
      .finally(() => setLoading(false))
  }, [])

  const login = async (email: string, password: string) => {
    const tokens = await api.login(email, password)
    applyTokens(tokens.access_token, tokens.refresh_token, tokens.organization_id)
    const me = await api.me()
    setUser(me)
    return tokens.organization_id
  }

  const register = async (email: string, password: string, fullName?: string) => {
    await api.register(email, password, fullName)
    return login(email, password)
  }

  const logout = () => {
    clearTokens()
    setUser(null)
    setOrganizationId(null)
    queryClient.clear()
  }

  const switchOrganization = async (orgId: string) => {
    const tokens = await api.switchOrg(orgId)
    applyTokens(tokens.access_token, tokens.refresh_token, tokens.organization_id)
    queryClient.clear()
  }

  const setOrganizationFromTokens = (access: string, refresh: string, orgId?: string | null) => {
    applyTokens(access, refresh, orgId)
    queryClient.clear()
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        organizationId,
        hasOrganization: !!organizationId,
        loading,
        login,
        register,
        logout,
        switchOrganization,
        setOrganizationFromTokens,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}

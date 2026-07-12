import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './hooks/useAuth'
import { LoginPage } from './pages/LoginPage'
import { RegisterPage } from './pages/RegisterPage'
import { OnboardingPage } from './pages/OnboardingPage'
import { DashboardPage } from './pages/DashboardPage'
import { ProjectsPage } from './pages/ProjectsPage'
import { ProjectDetailPage } from './pages/ProjectDetailPage'
import { PromptDetailPage } from './pages/PromptDetailPage'
import { MembersPage } from './pages/MembersPage'
import { ProvidersPage } from './pages/ProvidersPage'
import { SettingsPage } from './pages/SettingsPage'

function LoadingScreen() {
  return <div className="flex min-h-screen items-center justify-center text-slate">Loading...</div>
}

function OnboardingRoute({ children }: { children: React.ReactNode }) {
  const { user, hasOrganization, loading } = useAuth()
  if (loading) return <LoadingScreen />
  if (!user) return <Navigate to="/login" replace />
  if (hasOrganization) return <Navigate to="/" replace />
  return <>{children}</>
}

function OrgRequiredRoute({ children }: { children: React.ReactNode }) {
  const { user, hasOrganization, loading } = useAuth()
  if (loading) return <LoadingScreen />
  if (!user) return <Navigate to="/login" replace />
  if (!hasOrganization) return <Navigate to="/onboarding" replace />
  return <>{children}</>
}

function PublicRoute({ children }: { children: React.ReactNode }) {
  const { user, hasOrganization, loading } = useAuth()
  if (loading) return <LoadingScreen />
  if (user) return <Navigate to={hasOrganization ? '/' : '/onboarding'} replace />
  return <>{children}</>
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
      <Route path="/register" element={<PublicRoute><RegisterPage /></PublicRoute>} />
      <Route path="/onboarding" element={<OnboardingRoute><OnboardingPage /></OnboardingRoute>} />
      <Route path="/" element={<OrgRequiredRoute><DashboardPage /></OrgRequiredRoute>} />
      <Route path="/projects" element={<OrgRequiredRoute><ProjectsPage /></OrgRequiredRoute>} />
      <Route path="/projects/:projectId" element={<OrgRequiredRoute><ProjectDetailPage /></OrgRequiredRoute>} />
      <Route path="/prompts/:promptId" element={<OrgRequiredRoute><PromptDetailPage /></OrgRequiredRoute>} />
      <Route path="/members" element={<OrgRequiredRoute><MembersPage /></OrgRequiredRoute>} />
      <Route path="/providers" element={<OrgRequiredRoute><ProvidersPage /></OrgRequiredRoute>} />
      <Route path="/settings" element={<OrgRequiredRoute><SettingsPage /></OrgRequiredRoute>} />
    </Routes>
  )
}

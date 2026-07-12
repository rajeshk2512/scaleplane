import { FormEvent, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ApiError } from '../api/client'
import { useAuth } from '../hooks/useAuth'
import { Button } from '../components/Button'
import { Input } from '../components/Input'
import { Card } from '../components/Card'

export function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    try {
      const orgId = await login(email, password)
      navigate(orgId ? '/' : '/onboarding')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Login failed')
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-cloud px-4">
      <Card className="w-full max-w-md">
        <div className="mb-6 flex flex-col items-center gap-3">
          <img src="/logo.svg" alt="ScalePlane" className="h-16 w-16" />
          <h1 className="font-display text-2xl font-bold text-navy">Sign in to ScalePlane</h1>
          <p className="text-center text-sm text-slate">Enterprise infrastructure for agentic systems</p>
        </div>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <Input label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          {error && <p className="text-sm text-alert">{error}</p>}
          <Button type="submit" className="w-full">Sign in</Button>
        </form>
        <p className="mt-4 text-center text-sm text-slate">
          No account? <Link to="/register" className="text-teal hover:underline">Register</Link>
        </p>
      </Card>
    </div>
  )
}

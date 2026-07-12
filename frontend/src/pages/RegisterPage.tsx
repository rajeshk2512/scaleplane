import { FormEvent, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ApiError } from '../api/client'
import { useAuth } from '../hooks/useAuth'
import { Button } from '../components/Button'
import { Input } from '../components/Input'
import { Card } from '../components/Card'

export function RegisterPage() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    try {
      await register(email, password, fullName || undefined)
      navigate('/')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Registration failed')
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-cloud px-4">
      <Card className="w-full max-w-md">
        <div className="mb-6 flex flex-col items-center gap-3">
          <img src="/logo.svg" alt="ScalePlane" className="h-16 w-16" />
          <h1 className="font-display text-2xl font-bold text-navy">Create your account</h1>
        </div>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <Input label="Full name" value={fullName} onChange={(e) => setFullName(e.target.value)} />
          <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <Input label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8} />
          {error && <p className="text-sm text-alert">{error}</p>}
          <Button type="submit" className="w-full">Create account</Button>
        </form>
        <p className="mt-4 text-center text-sm text-slate">
          Already have an account? <Link to="/login" className="text-teal hover:underline">Sign in</Link>
        </p>
      </Card>
    </div>
  )
}

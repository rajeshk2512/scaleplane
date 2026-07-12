import { FormEvent, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ApiError, api } from '../api/client'
import { useAuth } from '../hooks/useAuth'
import { Button } from '../components/Button'
import { Input } from '../components/Input'
import { Card } from '../components/Card'

function slugify(value: string): string {
  return value
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 100)
}

export function OnboardingPage() {
  const { setOrganizationFromTokens } = useAuth()
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [slug, setSlug] = useState('')
  const [slugTouched, setSlugTouched] = useState(false)
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    if (!slugTouched) {
      setSlug(slugify(name))
    }
  }, [name, slugTouched])

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      const result = await api.createOrg(name, slug)
      setOrganizationFromTokens(
        result.tokens.access_token,
        result.tokens.refresh_token,
        result.tokens.organization_id,
      )
      navigate('/')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to create organization')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-cloud px-4">
      <Card className="w-full max-w-md">
        <div className="mb-6 flex flex-col items-center gap-3">
          <img src="/logo.svg" alt="ScalePlane" className="h-16 w-16" />
          <h1 className="font-display text-2xl font-bold text-navy">Create your organization</h1>
          <p className="text-center text-sm text-slate">
            Set up your workspace to start managing prompts and projects.
          </p>
        </div>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <Input
            label="Organization name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
          <Input
            label="Slug"
            value={slug}
            onChange={(e) => {
              setSlugTouched(true)
              setSlug(e.target.value)
            }}
            pattern="^[a-z0-9-]+$"
            required
          />
          <p className="text-xs text-slate">Lowercase letters, numbers, and hyphens only.</p>
          {error && <p className="text-sm text-alert">{error}</p>}
          <Button type="submit" className="w-full" disabled={submitting}>
            {submitting ? 'Creating...' : 'Create organization'}
          </Button>
        </form>
      </Card>
    </div>
  )
}

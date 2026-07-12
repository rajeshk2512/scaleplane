import { FormEvent, useEffect, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ApiError, api } from '../api/client'
import { AppLayout } from '../components/AppLayout'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { Input } from '../components/Input'
import { useAuth } from '../hooks/useAuth'

function slugify(value: string): string {
  return value
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 100)
}

export function SettingsPage() {
  const { setOrganizationFromTokens } = useAuth()
  const queryClient = useQueryClient()
  const [name, setName] = useState('')
  const [slug, setSlug] = useState('')
  const [error, setError] = useState('')
  const [showCreateOrg, setShowCreateOrg] = useState(false)
  const [newOrgName, setNewOrgName] = useState('')
  const [newOrgSlug, setNewOrgSlug] = useState('')
  const [newOrgSlugTouched, setNewOrgSlugTouched] = useState(false)
  const [createError, setCreateError] = useState('')

  const { data: org } = useQuery({ queryKey: ['org'], queryFn: api.currentOrg })
  const { data: orgs = [] } = useQuery({ queryKey: ['organizations'], queryFn: api.listOrgs })

  const canEdit = orgs.find((item) => item.id === org?.id)?.role === 'owner'
    || orgs.find((item) => item.id === org?.id)?.role === 'admin'

  useEffect(() => {
    if (org) {
      setName(org.name)
      setSlug(org.slug)
    }
  }, [org])

  useEffect(() => {
    if (!newOrgSlugTouched) {
      setNewOrgSlug(slugify(newOrgName))
    }
  }, [newOrgName, newOrgSlugTouched])

  const updateMutation = useMutation({
    mutationFn: () => api.updateOrg({ name, slug }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['org'] })
      queryClient.invalidateQueries({ queryKey: ['organizations'] })
      setError('')
    },
    onError: (err) => {
      setError(err instanceof ApiError ? err.message : 'Failed to update organization')
    },
  })

  const handleUpdate = (e: FormEvent) => {
    e.preventDefault()
    updateMutation.mutate()
  }

  const handleCreateOrg = async (e: FormEvent) => {
    e.preventDefault()
    setCreateError('')
    try {
      const result = await api.createOrg(newOrgName, newOrgSlug)
      setOrganizationFromTokens(
        result.tokens.access_token,
        result.tokens.refresh_token,
        result.tokens.organization_id,
      )
      setShowCreateOrg(false)
      setNewOrgName('')
      setNewOrgSlug('')
      setNewOrgSlugTouched(false)
      queryClient.invalidateQueries({ queryKey: ['organizations'] })
      queryClient.invalidateQueries({ queryKey: ['org'] })
    } catch (err) {
      setCreateError(err instanceof ApiError ? err.message : 'Failed to create organization')
    }
  }

  return (
    <AppLayout>
      <div className="mb-8">
        <h1 className="font-display text-3xl font-bold text-navy">Settings</h1>
        <p className="mt-1 text-slate">Organization and CLI configuration</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <h2 className="mb-4 font-display text-lg font-medium text-navy">Organization</h2>
          {canEdit ? (
            <form onSubmit={handleUpdate} className="flex flex-col gap-4">
              <Input label="Name" value={name} onChange={(e) => setName(e.target.value)} required />
              <Input
                label="Slug"
                value={slug}
                onChange={(e) => setSlug(e.target.value)}
                pattern="^[a-z0-9-]+$"
                required
              />
              {error && <p className="text-sm text-alert">{error}</p>}
              <Button type="submit" disabled={updateMutation.isPending}>
                {updateMutation.isPending ? 'Saving...' : 'Save changes'}
              </Button>
            </form>
          ) : (
            <dl className="space-y-3 text-sm">
              <div>
                <dt className="text-slate">Name</dt>
                <dd className="font-medium text-navy">{org?.name ?? '—'}</dd>
              </div>
              <div>
                <dt className="text-slate">Slug</dt>
                <dd className="font-mono text-navy">{org?.slug ?? '—'}</dd>
              </div>
            </dl>
          )}

          <div className="mt-6 border-t border-mist pt-4">
            <Button variant="ghost" onClick={() => setShowCreateOrg((value) => !value)}>
              {showCreateOrg ? 'Cancel' : 'Create another organization'}
            </Button>
            {showCreateOrg && (
              <form onSubmit={handleCreateOrg} className="mt-4 flex flex-col gap-3">
                <Input
                  label="Organization name"
                  value={newOrgName}
                  onChange={(e) => setNewOrgName(e.target.value)}
                  required
                />
                <Input
                  label="Slug"
                  value={newOrgSlug}
                  onChange={(e) => {
                    setNewOrgSlugTouched(true)
                    setNewOrgSlug(e.target.value)
                  }}
                  pattern="^[a-z0-9-]+$"
                  required
                />
                {createError && <p className="text-sm text-alert">{createError}</p>}
                <Button type="submit">Create organization</Button>
              </form>
            )}
          </div>
        </Card>

        <Card>
          <h2 className="mb-4 font-display text-lg font-medium text-navy">CLI configuration</h2>
          <p className="mb-3 text-sm text-slate">
            Point the ScalePlane CLI at your local API:
          </p>
          <pre className="rounded-brand bg-cloud p-4 font-mono text-xs text-navy">
{`scaleplane config set api_url http://127.0.0.1:8000/api/v1
scaleplane auth login`}
          </pre>
        </Card>
      </div>
    </AppLayout>
  )
}

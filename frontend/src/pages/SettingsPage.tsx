import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import { AppLayout } from '../components/AppLayout'
import { Card } from '../components/Card'

export function SettingsPage() {
  const { data: org } = useQuery({ queryKey: ['org'], queryFn: api.currentOrg })

  return (
    <AppLayout>
      <div className="mb-8">
        <h1 className="font-display text-3xl font-bold text-navy">Settings</h1>
        <p className="mt-1 text-slate">Organization and CLI configuration</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <h2 className="mb-4 font-display text-lg font-medium text-navy">Organization</h2>
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

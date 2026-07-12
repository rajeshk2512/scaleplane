import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import { AppLayout } from '../components/AppLayout'
import { Badge } from '../components/Badge'
import { Button } from '../components/Button'
import { Card } from '../components/Card'

export function DashboardPage() {
  const { data: org } = useQuery({ queryKey: ['org'], queryFn: api.currentOrg })
  const { data: projects = [] } = useQuery({ queryKey: ['projects'], queryFn: api.listProjects })

  return (
    <AppLayout>
      <div className="mb-8">
        <h1 className="font-display text-3xl font-bold text-navy">Dashboard</h1>
        <p className="mt-1 text-slate">{org?.name ?? 'Loading organization...'}</p>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <Card>
          <p className="text-sm text-slate">Projects</p>
          <p className="mt-2 font-display text-3xl font-bold text-navy">{projects.length}</p>
        </Card>
        <Card>
          <p className="text-sm text-slate">Organization</p>
          <p className="mt-2 font-display text-xl font-bold text-navy">{org?.slug}</p>
        </Card>
        <Card>
          <p className="text-sm text-slate">Phase</p>
          <Badge variant="teal">Prompt Versioning</Badge>
        </Card>
      </div>

      <Card className="mt-8">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="font-display text-xl font-medium text-navy">Recent projects</h2>
          <Link to="/projects">
            <Button variant="primary">View projects</Button>
          </Link>
        </div>
        {projects.length === 0 ? (
          <p className="text-sm text-slate">No projects yet. Create your first project to get started.</p>
        ) : (
          <ul className="divide-y divide-mist">
            {projects.slice(0, 5).map((p) => (
              <li key={p.id} className="flex items-center justify-between py-3">
                <div>
                  <Link to={`/projects/${p.id}`} className="font-medium text-teal hover:underline">
                    {p.name}
                  </Link>
                  <p className="text-xs text-slate">{p.slug}</p>
                </div>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </AppLayout>
  )
}

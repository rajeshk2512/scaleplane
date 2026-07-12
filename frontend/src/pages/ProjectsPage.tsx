import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { FormEvent, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import { AppLayout } from '../components/AppLayout'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { Input } from '../components/Input'

export function ProjectsPage() {
  const queryClient = useQueryClient()
  const { data: projects = [], isLoading } = useQuery({ queryKey: ['projects'], queryFn: api.listProjects })
  const [name, setName] = useState('')
  const [slug, setSlug] = useState('')
  const [showForm, setShowForm] = useState(false)

  const createMutation = useMutation({
    mutationFn: () => api.createProject(name, slug),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      setName('')
      setSlug('')
      setShowForm(false)
    },
  })

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    createMutation.mutate()
  }

  return (
    <AppLayout>
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="font-display text-3xl font-bold text-navy">Projects</h1>
          <p className="mt-1 text-slate">Organize prompts by project</p>
        </div>
        {!showForm && (
          <Button onClick={() => setShowForm(true)}>New project</Button>
        )}
      </div>

      {showForm && (
        <Card className="mb-6">
          <form onSubmit={handleSubmit} className="flex flex-col gap-4 md:flex-row md:items-end">
            <Input label="Name" value={name} onChange={(e) => setName(e.target.value)} required className="flex-1" />
            <Input
              label="Slug"
              value={slug}
              onChange={(e) => setSlug(e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, ''))}
              required
              pattern="^[a-z0-9-]+$"
              className="flex-1"
            />
            <div className="flex gap-2">
              <Button type="submit" disabled={createMutation.isPending}>Create</Button>
              <Button type="button" variant="ghost" onClick={() => setShowForm(false)}>Cancel</Button>
            </div>
          </form>
        </Card>
      )}

      <Card>
        {isLoading ? (
          <p className="text-slate">Loading...</p>
        ) : projects.length === 0 ? (
          <p className="text-slate">No projects yet.</p>
        ) : (
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-mist text-slate">
                <th className="pb-3 font-medium">Name</th>
                <th className="pb-3 font-medium">Slug</th>
                <th className="pb-3 font-medium">Created</th>
              </tr>
            </thead>
            <tbody>
              {projects.map((p) => (
                <tr key={p.id} className="border-b border-mist last:border-0">
                  <td className="py-3">
                    <Link to={`/projects/${p.id}`} className="font-medium text-teal hover:underline">
                      {p.name}
                    </Link>
                  </td>
                  <td className="py-3 font-mono text-xs text-slate">{p.slug}</td>
                  <td className="py-3 text-slate">{new Date(p.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>
    </AppLayout>
  )
}

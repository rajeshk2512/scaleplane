import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { FormEvent, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api/client'
import { AppLayout } from '../components/AppLayout'
import { Badge } from '../components/Badge'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { Input } from '../components/Input'

export function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const queryClient = useQueryClient()
  const { data: prompts = [], isLoading } = useQuery({
    queryKey: ['prompts', projectId],
    queryFn: () => api.listPrompts(projectId!),
    enabled: !!projectId,
  })

  const [showForm, setShowForm] = useState(false)
  const [name, setName] = useState('')
  const [slug, setSlug] = useState('')
  const [content, setContent] = useState('')

  const createMutation = useMutation({
    mutationFn: () => api.createPrompt(projectId!, { name, slug, content }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['prompts', projectId] })
      setName('')
      setSlug('')
      setContent('')
      setShowForm(false)
    },
  })

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    createMutation.mutate()
  }

  return (
    <AppLayout>
      <div className="mb-4">
        <Link to="/projects" className="text-sm text-teal hover:underline">← Projects</Link>
      </div>
      <div className="mb-8 flex items-center justify-between">
        <h1 className="font-display text-3xl font-bold text-navy">Prompts</h1>
        {!showForm && <Button onClick={() => setShowForm(true)}>New prompt</Button>}
      </div>

      {showForm && (
        <Card className="mb-6">
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div className="grid gap-4 md:grid-cols-2">
              <Input label="Name" value={name} onChange={(e) => setName(e.target.value)} required />
              <Input
                label="Slug"
                value={slug}
                onChange={(e) => setSlug(e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, ''))}
                required
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-navy">Initial content</label>
              <textarea
                className="min-h-[120px] w-full rounded-brand border border-mist p-3 font-mono text-sm"
                value={content}
                onChange={(e) => setContent(e.target.value)}
                required
              />
            </div>
            <div className="flex gap-2">
              <Button type="submit" disabled={createMutation.isPending}>Create prompt</Button>
              <Button type="button" variant="ghost" onClick={() => setShowForm(false)}>Cancel</Button>
            </div>
          </form>
        </Card>
      )}

      <Card>
        {isLoading ? (
          <p className="text-slate">Loading...</p>
        ) : prompts.length === 0 ? (
          <p className="text-slate">No prompts in this project.</p>
        ) : (
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-mist text-slate">
                <th className="pb-3 font-medium">Name</th>
                <th className="pb-3 font-medium">Latest version</th>
                <th className="pb-3 font-medium">Production</th>
              </tr>
            </thead>
            <tbody>
              {prompts.map((p) => (
                <tr key={p.id} className="border-b border-mist last:border-0">
                  <td className="py-3">
                    <Link to={`/prompts/${p.id}`} className="font-medium text-teal hover:underline">
                      {p.name}
                    </Link>
                    <p className="font-mono text-xs text-slate">{p.slug}</p>
                  </td>
                  <td className="py-3">v{p.latest_version_number ?? '—'}</td>
                  <td className="py-3">
                    {p.production_tag_version ? (
                      <Badge variant="amber">v{p.production_tag_version}</Badge>
                    ) : (
                      <span className="text-slate">—</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>
    </AppLayout>
  )
}

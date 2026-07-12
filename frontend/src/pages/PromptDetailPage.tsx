import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { FormEvent, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api, ENVIRONMENT_TAGS, EnvironmentTag } from '../api/client'
import { AppLayout } from '../components/AppLayout'
import { Badge } from '../components/Badge'
import { Button } from '../components/Button'
import { Card } from '../components/Card'

const TAG_LABELS: Record<EnvironmentTag, string> = {
  production: 'Production',
  staging: 'Staging',
  dev: 'Dev',
}

export function PromptDetailPage() {
  const { promptId } = useParams<{ promptId: string }>()
  const queryClient = useQueryClient()

  const { data: prompt } = useQuery({
    queryKey: ['prompt', promptId],
    queryFn: () => api.getPrompt(promptId!),
    enabled: !!promptId,
  })

  const { data: versions = [] } = useQuery({
    queryKey: ['versions', promptId],
    queryFn: () => api.listVersions(promptId!),
    enabled: !!promptId,
  })

  const [newContent, setNewContent] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [selectedTag, setSelectedTag] = useState<EnvironmentTag>('staging')
  const [resolved, setResolved] = useState<{ tag: EnvironmentTag; content: string } | null>(null)

  const createVersion = useMutation({
    mutationFn: () => api.createVersion(promptId!, newContent),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['versions', promptId] })
      queryClient.invalidateQueries({ queryKey: ['prompt', promptId] })
      setNewContent('')
      setShowForm(false)
    },
  })

  const promote = useMutation({
    mutationFn: ({ versionNumber, tag }: { versionNumber: number; tag: EnvironmentTag }) =>
      api.promoteTag(promptId!, tag, versionNumber),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['prompt', promptId] })
    },
  })

  const resolve = useMutation({
    mutationFn: (tag: EnvironmentTag) => api.resolvePrompt(promptId!, tag),
    onSuccess: (data, tag) => setResolved({ tag, content: data.content }),
  })

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    createVersion.mutate()
  }

  return (
    <AppLayout>
      <div className="mb-4">
        {prompt && (
          <Link to={`/projects/${prompt.project_id}`} className="text-sm text-teal hover:underline">
            ← Back to project
          </Link>
        )}
      </div>

      <div className="mb-8 flex items-start justify-between">
        <div>
          <h1 className="font-display text-3xl font-bold text-navy">{prompt?.name ?? 'Prompt'}</h1>
          <p className="mt-1 font-mono text-sm text-slate">{prompt?.slug}</p>
          <div className="mt-2 flex flex-wrap gap-2">
            {ENVIRONMENT_TAGS.map((tag) => {
              const version = prompt?.environment_tags?.[tag]
              return (
                <Badge key={tag} variant={tag === 'production' ? 'amber' : 'teal'}>
                  {tag} → {version ? `v${version}` : '—'}
                </Badge>
              )
            })}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={selectedTag}
            onChange={(e) => setSelectedTag(e.target.value as EnvironmentTag)}
            className="min-h-[44px] rounded-brand border border-mist bg-white px-3 py-2 text-sm text-navy outline-none focus:border-teal"
          >
            {ENVIRONMENT_TAGS.map((tag) => (
              <option key={tag} value={tag}>
                {TAG_LABELS[tag]}
              </option>
            ))}
          </select>
          <Button variant="ghost" onClick={() => resolve.mutate(selectedTag)}>
            Resolve {TAG_LABELS[selectedTag].toLowerCase()}
          </Button>
          {!showForm && <Button onClick={() => setShowForm(true)}>New version</Button>}
        </div>
      </div>

      {resolved && (
        <Card className="mb-6">
          <h2 className="mb-2 font-display text-lg font-medium text-navy">
            Resolved content ({resolved.tag})
          </h2>
          <pre className="whitespace-pre-wrap rounded-brand bg-cloud p-4 font-mono text-sm text-navy">
            {resolved.content}
          </pre>
        </Card>
      )}

      {showForm && (
        <Card className="mb-6">
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div>
              <label className="mb-1 block text-sm font-medium text-navy">Version content</label>
              <textarea
                className="min-h-[160px] w-full rounded-brand border border-mist p-3 font-mono text-sm"
                value={newContent}
                onChange={(e) => setNewContent(e.target.value)}
                required
              />
            </div>
            <div className="flex gap-2">
              <Button type="submit" disabled={createVersion.isPending}>Save version</Button>
              <Button type="button" variant="ghost" onClick={() => setShowForm(false)}>Cancel</Button>
            </div>
          </form>
        </Card>
      )}

      <Card>
        <h2 className="mb-4 font-display text-xl font-medium text-navy">Version history</h2>
        {versions.length === 0 ? (
          <p className="text-slate">No versions yet.</p>
        ) : (
          <ul className="space-y-4">
            {versions.map((v) => (
              <li key={v.id} className="rounded-brand border border-mist p-4">
                <div className="mb-2 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-display font-medium text-navy">v{v.version_number}</span>
                    <span className="text-xs text-slate">{new Date(v.created_at).toLocaleString()}</span>
                  </div>
                  <Button
                    variant="ghost"
                    className="!min-h-0 !py-1 !text-xs"
                    onClick={() => promote.mutate({ versionNumber: v.version_number, tag: selectedTag })}
                  >
                    Promote to {selectedTag}
                  </Button>
                </div>
                <pre className="max-h-40 overflow-auto whitespace-pre-wrap font-mono text-xs text-slate">
                  {v.content}
                </pre>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </AppLayout>
  )
}

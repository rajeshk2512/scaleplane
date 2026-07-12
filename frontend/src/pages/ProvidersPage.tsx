import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { FormEvent, useState } from 'react'
import { api, Provider } from '../api/client'
import { AppLayout } from '../components/AppLayout'
import { Badge } from '../components/Badge'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { Input } from '../components/Input'

export function ProvidersPage() {
  const queryClient = useQueryClient()
  const { data: providers = [] } = useQuery({ queryKey: ['providers'], queryFn: api.listProviders })
  const [name, setName] = useState('')
  const [providerType, setProviderType] = useState<Provider['provider_type']>('openai')
  const [showForm, setShowForm] = useState(false)

  const createMutation = useMutation({
    mutationFn: () => api.createProvider(name, providerType, {}),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['providers'] })
      setName('')
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
          <h1 className="font-display text-3xl font-bold text-navy">Providers</h1>
          <p className="mt-1 text-slate">Configure model providers for future SLM routing</p>
        </div>
        {!showForm && <Button onClick={() => setShowForm(true)}>Add provider</Button>}
      </div>

      <Card className="mb-6 border-teal/30 bg-teal/5">
        <div className="flex items-center gap-3">
          <Badge variant="teal">Coming soon</Badge>
          <p className="text-sm text-navy">
            SLM / frontier routing and completion proxy are stubbed in the MVP. Provider configs are stored for future gateway integration.
          </p>
        </div>
      </Card>

      {showForm && (
        <Card className="mb-6">
          <form onSubmit={handleSubmit} className="flex flex-col gap-4 md:flex-row md:items-end">
            <Input label="Name" value={name} onChange={(e) => setName(e.target.value)} required className="flex-1" />
            <div className="flex flex-col gap-1">
              <label className="text-sm font-medium text-navy">Type</label>
              <select
                className="min-h-[44px] rounded-brand border border-mist px-3 text-sm"
                value={providerType}
                onChange={(e) => setProviderType(e.target.value as Provider['provider_type'])}
              >
                <option value="openai">OpenAI</option>
                <option value="anthropic">Anthropic</option>
                <option value="local_slm">Local SLM</option>
              </select>
            </div>
            <div className="flex gap-2">
              <Button type="submit">Save</Button>
              <Button type="button" variant="ghost" onClick={() => setShowForm(false)}>Cancel</Button>
            </div>
          </form>
        </Card>
      )}

      <Card>
        {providers.length === 0 ? (
          <p className="text-slate">No providers configured yet.</p>
        ) : (
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-mist text-slate">
                <th className="pb-3 font-medium">Name</th>
                <th className="pb-3 font-medium">Type</th>
                <th className="pb-3 font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {providers.map((p) => (
                <tr key={p.id} className="border-b border-mist last:border-0">
                  <td className="py-3 font-medium">{p.name}</td>
                  <td className="py-3 font-mono text-xs">{p.provider_type}</td>
                  <td className="py-3">
                    <Badge variant={p.is_active ? 'teal' : 'default'}>
                      {p.is_active ? 'Active' : 'Inactive'}
                    </Badge>
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

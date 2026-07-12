import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { FormEvent, useState } from 'react'
import { api, Member } from '../api/client'
import { AppLayout } from '../components/AppLayout'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { Input } from '../components/Input'

const roles: Member['role'][] = ['admin', 'editor', 'viewer']

export function MembersPage() {
  const queryClient = useQueryClient()
  const { data: members = [], isLoading } = useQuery({ queryKey: ['members'], queryFn: api.listMembers })
  const [email, setEmail] = useState('')
  const [role, setRole] = useState<Member['role']>('viewer')
  const [showForm, setShowForm] = useState(false)

  const addMutation = useMutation({
    mutationFn: () => api.addMember(email, role),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['members'] })
      setEmail('')
      setShowForm(false)
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ userId, newRole }: { userId: string; newRole: Member['role'] }) =>
      api.updateMember(userId, newRole),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['members'] }),
  })

  const deleteMutation = useMutation({
    mutationFn: (userId: string) => api.deleteMember(userId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['members'] }),
  })

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    addMutation.mutate()
  }

  return (
    <AppLayout>
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="font-display text-3xl font-bold text-navy">Members & Roles</h1>
          <p className="mt-1 text-slate">Manage organization access and RBAC</p>
        </div>
        {!showForm && <Button onClick={() => setShowForm(true)}>Add member</Button>}
      </div>

      {showForm && (
        <Card className="mb-6">
          <form onSubmit={handleSubmit} className="flex flex-col gap-4 md:flex-row md:items-end">
            <Input
              label="Email (user must be registered)"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="flex-1"
            />
            <div className="flex flex-col gap-1">
              <label className="text-sm font-medium text-navy">Role</label>
              <select
                className="min-h-[44px] rounded-brand border border-mist px-3 text-sm"
                value={role}
                onChange={(e) => setRole(e.target.value as Member['role'])}
              >
                {roles.map((r) => (
                  <option key={r} value={r}>{r}</option>
                ))}
              </select>
            </div>
            <div className="flex gap-2">
              <Button type="submit">Add</Button>
              <Button type="button" variant="ghost" onClick={() => setShowForm(false)}>Cancel</Button>
            </div>
          </form>
        </Card>
      )}

      <Card>
        {isLoading ? (
          <p className="text-slate">Loading...</p>
        ) : (
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-mist text-slate">
                <th className="pb-3 font-medium">Email</th>
                <th className="pb-3 font-medium">Name</th>
                <th className="pb-3 font-medium">Role</th>
                <th className="pb-3 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {members.map((m) => (
                <tr key={m.id} className="border-b border-mist last:border-0">
                  <td className="py-3">{m.email}</td>
                  <td className="py-3 text-slate">{m.full_name ?? '—'}</td>
                  <td className="py-3">
                    {m.role === 'owner' ? (
                      <span className="font-medium capitalize">{m.role}</span>
                    ) : (
                      <select
                        className="rounded-brand border border-mist px-2 py-1 text-sm"
                        value={m.role}
                        onChange={(e) =>
                          updateMutation.mutate({ userId: m.user_id, newRole: e.target.value as Member['role'] })
                        }
                      >
                        {roles.map((r) => (
                          <option key={r} value={r}>{r}</option>
                        ))}
                      </select>
                    )}
                  </td>
                  <td className="py-3">
                    {m.role !== 'owner' && (
                      <Button
                        variant="danger"
                        className="!min-h-0 !px-2 !py-1 !text-xs"
                        onClick={() => deleteMutation.mutate(m.user_id)}
                      >
                        Remove
                      </Button>
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

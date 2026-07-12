const API_BASE = import.meta.env.VITE_API_URL || '/api/v1'

export interface User {
  id: string
  email: string
  full_name: string | null
  created_at: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface Organization {
  id: string
  slug: string
  name: string
  is_default: boolean
  created_at: string
}

export interface Project {
  id: string
  organization_id: string
  name: string
  slug: string
  description: string | null
  created_at: string
}

export interface Prompt {
  id: string
  project_id: string
  organization_id: string
  name: string
  slug: string
  description: string | null
  created_at: string
  latest_version_number: number | null
  production_tag_version: number | null
}

export interface PromptVersion {
  id: string
  prompt_id: string
  version_number: number
  content: string
  content_hash: string
  metadata: Record<string, unknown> | null
  parent_version_id: string | null
  created_by_id: string | null
  created_at: string
}

export interface Member {
  id: string
  user_id: string
  email: string
  full_name: string | null
  role: 'owner' | 'admin' | 'editor' | 'viewer'
  created_at: string
}

export interface Provider {
  id: string
  organization_id: string
  name: string
  provider_type: 'openai' | 'anthropic' | 'local_slm'
  config: Record<string, unknown>
  is_active: boolean
  created_at: string
}

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message)
  }
}

function getToken(): string | null {
  return localStorage.getItem('access_token')
}

export function setTokens(access: string, refresh: string) {
  localStorage.setItem('access_token', access)
  localStorage.setItem('refresh_token', refresh)
}

export function clearTokens() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  }
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers })
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }))
    throw new ApiError(res.status, body.detail || res.statusText)
  }
  if (res.status === 204) return undefined as T
  return res.json()
}

export const api = {
  register: (email: string, password: string, full_name?: string) =>
    request<User>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, full_name }),
    }),

  login: (email: string, password: string) =>
    request<TokenResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),

  me: () => request<User>('/users/me'),

  currentOrg: () => request<Organization>('/organizations/current'),

  listMembers: () => request<Member[]>('/organizations/current/members'),

  addMember: (email: string, role: Member['role']) =>
    request<Member>('/organizations/current/members', {
      method: 'POST',
      body: JSON.stringify({ email, role }),
    }),

  updateMember: (userId: string, role: Member['role']) =>
    request<Member>(`/organizations/current/members/${userId}`, {
      method: 'PATCH',
      body: JSON.stringify({ role }),
    }),

  deleteMember: (userId: string) =>
    request<void>(`/organizations/current/members/${userId}`, { method: 'DELETE' }),

  listProjects: () => request<Project[]>('/projects'),

  createProject: (name: string, slug: string, description?: string) =>
    request<Project>('/projects', {
      method: 'POST',
      body: JSON.stringify({ name, slug, description }),
    }),

  listPrompts: (projectId: string) =>
    request<Prompt[]>(`/projects/${projectId}/prompts`),

  createPrompt: (
    projectId: string,
    data: { name: string; slug: string; content: string; description?: string }
  ) =>
    request<Prompt>(`/projects/${projectId}/prompts`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getPrompt: (promptId: string) => request<Prompt>(`/prompts/${promptId}`),

  listVersions: (promptId: string) =>
    request<PromptVersion[]>(`/prompts/${promptId}/versions`),

  createVersion: (promptId: string, content: string) =>
    request<PromptVersion>(`/prompts/${promptId}/versions`, {
      method: 'POST',
      body: JSON.stringify({ content }),
    }),

  promoteTag: (promptId: string, tag: string, versionNumber: number) =>
    request<{ version_number: number }>(
      `/prompts/${promptId}/tags/${tag}?version_number=${versionNumber}`,
      { method: 'PUT' }
    ),

  resolvePrompt: (promptId: string, tag = 'production') =>
    request<{ content: string; version_number: number }>(
      `/prompts/${promptId}/resolve?tag=${tag}`
    ),

  listProviders: () => request<Provider[]>('/providers'),

  createProvider: (name: string, provider_type: Provider['provider_type'], config: Record<string, unknown>) =>
    request<Provider>('/providers', {
      method: 'POST',
      body: JSON.stringify({ name, provider_type, config }),
    }),
}

export { ApiError }

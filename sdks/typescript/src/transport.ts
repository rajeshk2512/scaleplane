import type { AuthProvider } from './auth.js'
import type { ClientConfig } from './config.js'
import { ApiError } from './errors.js'

export type JsonValue = unknown

export class HttpTransport {
  constructor(
    private readonly config: ClientConfig,
    private readonly auth: AuthProvider,
  ) {}

  async request<T = JsonValue>(
    method: string,
    path: string,
    options: {
      params?: Record<string, string | number | undefined>
      body?: unknown
      acceptStatuses?: number[]
    } = {},
  ): Promise<T> {
    const url = new URL(`${this.config.baseUrl}${path}`)
    if (options.params) {
      for (const [key, value] of Object.entries(options.params)) {
        if (value !== undefined) {
          url.searchParams.set(key, String(value))
        }
      }
    }

    const controller = new AbortController()
    const timer = setTimeout(() => controller.abort(), this.config.timeoutMs)
    try {
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
          ...this.auth.headers(),
        },
        body: options.body === undefined ? undefined : JSON.stringify(options.body),
        signal: controller.signal,
      })

      const accepted =
        response.status < 400 ||
        (options.acceptStatuses?.includes(response.status) ?? false)

      if (!accepted) {
        throw new ApiError(response.status, await extractDetail(response))
      }

      if (response.status === 204) {
        return undefined as T
      }
      const text = await response.text()
      if (!text) {
        return undefined as T
      }
      return JSON.parse(text) as T
    } finally {
      clearTimeout(timer)
    }
  }
}

async function extractDetail(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: unknown }
    if (body && typeof body.detail === 'string') {
      return body.detail
    }
    if (body?.detail !== undefined) {
      return String(body.detail)
    }
  } catch {
    // ignore
  }
  return response.statusText || 'Request failed'
}

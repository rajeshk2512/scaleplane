export interface ClientConfig {
  baseUrl: string
  timeoutMs: number
}

export function normalizeBaseUrl(baseUrl: string): string {
  return baseUrl.replace(/\/+$/, '')
}

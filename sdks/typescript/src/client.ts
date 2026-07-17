import { BearerTokenAuth, type AuthProvider } from './auth.js'
import { normalizeBaseUrl, type ClientConfig } from './config.js'
import { PromptsResource } from './resources/prompts.js'
import { RoutingResource } from './resources/routing.js'
import { HttpTransport } from './transport.js'

export interface ClientOptions {
  baseUrl?: string
  token?: string
  auth?: AuthProvider
  timeoutMs?: number
}

export class ScalePlaneClient {
  readonly prompts: PromptsResource
  readonly routing: RoutingResource

  constructor(options: ClientOptions = {}) {
    const auth =
      options.auth ??
      (options.token ? new BearerTokenAuth(options.token) : undefined)
    if (!auth) {
      throw new Error('Provide token or auth')
    }
    const config: ClientConfig = {
      baseUrl: normalizeBaseUrl(options.baseUrl ?? 'http://127.0.0.1:8000/api/v1'),
      timeoutMs: options.timeoutMs ?? 30_000,
    }
    const transport = new HttpTransport(config, auth)
    this.prompts = new PromptsResource(transport)
    this.routing = new RoutingResource(transport)
  }
}

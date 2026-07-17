import type { components } from '../generated/schema.js'
import type { HttpTransport } from '../transport.js'

export type CompletionRequest = components['schemas']['CompletionRequest']
export type CompletionNotImplementedResponse =
  components['schemas']['CompletionNotImplementedResponse']

export class RoutingResource {
  constructor(private readonly transport: HttpTransport) {}

  async completions(
    request: Partial<CompletionRequest> = {},
  ): Promise<CompletionNotImplementedResponse> {
    const body: CompletionRequest = {
      tag: request.tag ?? 'production',
      messages: request.messages ?? [],
      prompt_id: request.prompt_id ?? null,
      prompt_slug: request.prompt_slug ?? null,
      model: request.model ?? null,
    }
    return this.transport.request<CompletionNotImplementedResponse>(
      'POST',
      '/route/completions',
      { body, acceptStatuses: [501] },
    )
  }
}

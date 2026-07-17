import type { components } from '../generated/schema.js'
import { NotFoundError } from '../errors.js'
import type { HttpTransport } from '../transport.js'

export type PromptResolveResponse = components['schemas']['PromptResolveResponse']
export type PromptTagResponse = components['schemas']['PromptTagResponse']
export type PromptResponse = components['schemas']['PromptResponse']
export type ProjectResponse = components['schemas']['ProjectResponse']

export class PromptsResource {
  constructor(private readonly transport: HttpTransport) {}

  async resolve(promptId: string, options: { tag?: string } = {}): Promise<PromptResolveResponse> {
    const tag = options.tag ?? 'production'
    return this.transport.request<PromptResolveResponse>('GET', `/prompts/${promptId}/resolve`, {
      params: { tag },
    })
  }

  async promote(
    promptId: string,
    tag: string,
    options: { versionNumber?: number; versionId?: string } = {},
  ): Promise<PromptTagResponse> {
    return this.transport.request<PromptTagResponse>('PUT', `/prompts/${promptId}/tags/${tag}`, {
      params: {
        version_number: options.versionNumber,
        version_id: options.versionId,
      },
    })
  }

  async resolveBySlug(
    project: string,
    prompt: string,
    options: { tag?: string } = {},
  ): Promise<PromptResolveResponse> {
    const promptId = await this.lookupPromptId(project, prompt)
    return this.resolve(promptId, options)
  }

  async promoteBySlug(
    project: string,
    prompt: string,
    tag: string,
    options: { versionNumber?: number; versionId?: string } = {},
  ): Promise<PromptTagResponse> {
    const promptId = await this.lookupPromptId(project, prompt)
    return this.promote(promptId, tag, options)
  }

  private async lookupPromptId(project: string, promptSlug: string): Promise<string> {
    const projectId = await this.lookupProjectId(project)
    const prompts = await this.transport.request<PromptResponse[]>(
      'GET',
      `/projects/${projectId}/prompts`,
    )
    const match = prompts.find((p) => p.slug === promptSlug || p.id === promptSlug)
    if (!match) {
      throw new NotFoundError(`Prompt not found: ${promptSlug}`)
    }
    return match.id
  }

  private async lookupProjectId(project: string): Promise<string> {
    const projects = await this.transport.request<ProjectResponse[]>('GET', '/projects')
    const match = projects.find((p) => p.slug === project || p.id === project)
    if (!match) {
      throw new NotFoundError(`Project not found: ${project}`)
    }
    return match.id
  }
}

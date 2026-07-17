import { afterEach, describe, expect, it, vi } from 'vitest'
import { ApiError, NotFoundError, ScalePlaneClient } from '../src/index.js'

const BASE = 'https://api.example.test/api/v1'
const PROMPT_ID = '11111111-1111-1111-1111-111111111111'
const PROJECT_ID = '22222222-2222-2222-2222-222222222222'
const VERSION_ID = '33333333-3333-3333-3333-333333333333'

function jsonResponse(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

afterEach(() => {
  vi.unstubAllGlobals()
  vi.restoreAllMocks()
})

describe('ScalePlaneClient', () => {
  it('resolves a prompt', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse(200, {
        prompt_id: PROMPT_ID,
        prompt_slug: 'system',
        tag: 'production',
        version_id: VERSION_ID,
        version_number: 2,
        content: 'You are helpful.',
        content_hash: 'abc',
        metadata: null,
      }),
    )
    vi.stubGlobal('fetch', fetchMock)

    const client = new ScalePlaneClient({ baseUrl: BASE, token: 'test-token' })
    const result = await client.prompts.resolve(PROMPT_ID)

    expect(result.prompt_slug).toBe('system')
    expect(result.version_number).toBe(2)
    expect(fetchMock).toHaveBeenCalledOnce()
    const [url, init] = fetchMock.mock.calls[0]
    expect(String(url)).toContain(`/prompts/${PROMPT_ID}/resolve`)
    expect((init as RequestInit).headers).toMatchObject({
      Authorization: 'Bearer test-token',
    })
  })

  it('resolves by slug with lookups', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        jsonResponse(200, [
          {
            id: PROJECT_ID,
            organization_id: '00000000-0000-0000-0000-000000000000',
            name: 'Demo',
            slug: 'demo',
            description: null,
            created_at: '2026-01-01T00:00:00Z',
          },
        ]),
      )
      .mockResolvedValueOnce(
        jsonResponse(200, [
          {
            id: PROMPT_ID,
            project_id: PROJECT_ID,
            organization_id: '00000000-0000-0000-0000-000000000000',
            name: 'System',
            slug: 'system-prompt',
            description: null,
            created_at: '2026-01-01T00:00:00Z',
            latest_version_number: 1,
            production_tag_version: 1,
            environment_tags: { production: 1, staging: null, dev: null },
          },
        ]),
      )
      .mockResolvedValueOnce(
        jsonResponse(200, {
          prompt_id: PROMPT_ID,
          prompt_slug: 'system-prompt',
          tag: 'staging',
          version_id: VERSION_ID,
          version_number: 1,
          content: 'hi',
          content_hash: 'x',
          metadata: null,
        }),
      )
    vi.stubGlobal('fetch', fetchMock)

    const client = new ScalePlaneClient({ baseUrl: BASE, token: 't' })
    const result = await client.prompts.resolveBySlug('demo', 'system-prompt', { tag: 'staging' })
    expect(result.content).toBe('hi')
    expect(fetchMock).toHaveBeenCalledTimes(3)
  })

  it('throws NotFoundError for missing project', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse(200, [])))
    const client = new ScalePlaneClient({ baseUrl: BASE, token: 't' })
    await expect(client.prompts.resolveBySlug('missing', 'system')).rejects.toBeInstanceOf(
      NotFoundError,
    )
  })

  it('throws ApiError on 404', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(jsonResponse(404, { detail: 'Tag not found' })),
    )
    const client = new ScalePlaneClient({ baseUrl: BASE, token: 't' })
    await expect(client.prompts.resolve(PROMPT_ID)).rejects.toMatchObject({
      status: 404,
      detail: 'Tag not found',
    } satisfies Partial<ApiError>)
  })

  it('accepts 501 completions stub', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse(501, {
        detail: 'SLM routing is not enabled in the MVP',
        message: 'Provider routing and completion proxy will be available in a future release.',
        future_capabilities: ['Dynamic SLM / frontier model routing'],
      }),
    )
    vi.stubGlobal('fetch', fetchMock)
    const client = new ScalePlaneClient({ baseUrl: BASE, token: 't' })
    const result = await client.routing.completions({ prompt_slug: 'system' })
    expect(result.detail).toContain('not enabled')
  })

  it('requires token or auth', () => {
    expect(() => new ScalePlaneClient({ baseUrl: BASE })).toThrow(/token or auth/)
  })
})

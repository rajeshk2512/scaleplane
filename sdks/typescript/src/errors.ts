export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly detail: string,
  ) {
    super(`${status}: ${detail}`)
    this.name = 'ApiError'
  }
}

export class NotFoundError extends ApiError {
  constructor(detail: string, status = 404) {
    super(status, detail)
    this.name = 'NotFoundError'
  }
}

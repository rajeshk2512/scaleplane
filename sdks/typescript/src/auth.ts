export interface AuthProvider {
  headers(): Record<string, string>
}

export class BearerTokenAuth implements AuthProvider {
  constructor(private readonly token: string) {}

  headers(): Record<string, string> {
    return { Authorization: `Bearer ${this.token}` }
  }
}

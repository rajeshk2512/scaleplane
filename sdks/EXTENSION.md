# ScalePlane SDK extension playbook

Open/Closed Principle: **core transport/auth stay closed**; new backend features land by regenerating models and adding (or extending) a **resource module**.

## Layers

| Layer | Location | Rule |
|-------|----------|------|
| Core | `auth`, `config`, `transport`, `errors`, `client` | Rarely change |
| Generated | `*/_generated` or `*/generated` | Never hand-edit; overwrite via codegen |
| Resources | `resources/*` | Open for extension |

## Adding a backend feature to all SDKs

1. Implement the FastAPI route + Pydantic schemas under `backend/app/`.
2. Export the OpenAPI contract:

   ```bash
   make sdk-export
   ```

   Commit `sdks/openapi/scaleplane.openapi.json` if it changed.

3. Regenerate models:

   ```bash
   make sdk-generate
   ```

4. Add **one resource module** (or one method on an existing resource) in each language:

   - Python: `sdks/python/src/scaleplane/resources/<feature>.py`
   - TypeScript: `sdks/typescript/src/resources/<feature>.ts`
   - Java: `sdks/java/src/main/java/com/scaleplane/resources/<Feature>Resource.java`

   Use generated types for request/response bodies. Call `HttpTransport` only — do not add HTTP logic to resources beyond path/params/body.

5. Mount the resource on the client facade (one line per language):

   - Python: `ScalePlaneClient.__init__`
   - TypeScript: `ScalePlaneClient` constructor
   - Java: `ScalePlaneClient` constructor

6. Add a mocked HTTP unit test in each SDK package.

7. Run:

   ```bash
   make sdk-test
   ```

## Runtime surface (v1)

Hand-written resources currently cover:

- `prompts.resolve` / `prompts.promote` / slug helpers
- `routing.completions` (accepts HTTP 501 stub response)

Admin APIs (orgs, members, auth) stay in the CLI/UI.

## Auth extension

Implement a new `AuthProvider` (e.g. API key headers) and pass it into the client constructor. Do not modify `HttpTransport` beyond reading `auth.headers()`.

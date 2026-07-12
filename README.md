# ScalePlane

Enterprise infrastructure for agentic systems — a control plane for git-like prompt versioning, RBAC, and future SLM/frontier model routing.

Phase 1 (MVP) delivers externalized prompt deployment with version history, tag promotion, user management, and routing extension points. Live inference and load balancing are stubbed for a future release.

## Monorepo structure

```
ScalePlane/
├── backend/     # Python 3.12 + FastAPI API
├── frontend/    # React 18 + TypeScript + Vite
├── cli/         # Python Typer CLI
├── assets/      # Brand logo and assets
├── docker-compose.yml
└── Makefile
```

## Prerequisites

- Python 3.12+
- Node.js 20+
- Docker (for PostgreSQL)

## Quick start

### 1. Start PostgreSQL

PostgreSQL runs on port **5433** by default (to avoid conflicts with a local Postgres on 5432).

```bash
docker compose up -d
```

### 2. Backend setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
alembic upgrade head
python -m app.seed   # optional demo data: owner@scaleplane.dev / password123
uvicorn app.main:app --reload --port 8000
```

API docs: http://127.0.0.1:8000/docs

### 3. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Web UI: http://localhost:5173

### 4. CLI setup

```bash
cd cli
../backend/.venv/bin/pip install -e .
scaleplane config set api_url http://127.0.0.1:8000/api/v1
scaleplane auth login
scaleplane orgs create --name "My Team" --slug my-team
scaleplane projects list
```

## CLI commands

| Command | Description |
|---------|-------------|
| `scaleplane auth login` | Authenticate with email/password |
| `scaleplane auth whoami` | Show current user |
| `scaleplane orgs list` | List organizations you belong to |
| `scaleplane orgs current` | Show active organization |
| `scaleplane orgs create --name X --slug x` | Create and activate an organization |
| `scaleplane orgs switch <id-or-slug>` | Switch active organization |
| `scaleplane projects list` | List projects |
| `scaleplane projects create --name X --slug x` | Create project |
| `scaleplane prompts list --project demo` | List prompts |
| `scaleplane prompts push file.txt --project demo --name "System"` | Push prompt version |
| `scaleplane prompts history system-prompt --project demo` | Version history |
| `scaleplane prompts promote system-prompt --project demo --version 2 --tag staging` | Promote version to an environment tag |
| `scaleplane prompts resolve system-prompt --project demo --tag staging` | Resolve tagged prompt content |

`promote` and `resolve` accept `--tag` / `-t` (default: `production`). Supported environment tags: `production`, `staging`, `dev`.

### Prompt tags

Versions are immutable snapshots; tags are movable pointers to a version. Creating a new version does not change what any tag serves until you promote.

Test a new version in staging before releasing to production:

```bash
scaleplane prompts push prompt-v2.txt --project demo --name "System"
scaleplane prompts promote system-prompt --project demo --version 2 --tag staging
scaleplane prompts resolve system-prompt --project demo --tag staging
# when satisfied:
scaleplane prompts promote system-prompt --project demo --version 2 --tag production
```

The latest version number and tagged versions are independent — `prompts list` shows both separately.

## API overview

- **Auth:** `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `POST /api/v1/auth/refresh`
- **Users:** `GET /api/v1/users/me`
- **Org & RBAC:** `GET /api/v1/organizations/current`, member CRUD
- **Prompts:** projects, versions, `PUT /prompts/{id}/tags/{tag}` (promote), `GET /prompts/{id}/resolve?tag=` (environment tags: `production`, `staging`, `dev`)
- **Routing (stub):** providers, routing policies, `POST /api/v1/route/completions` (501)

## RBAC roles

| Role | Capabilities |
|------|--------------|
| owner | Full org control |
| admin | Member management + all prompt ops |
| editor | Prompt create/edit/promote |
| viewer | Read-only |

## Brand

UI follows the ScalePlane Brand Identity Guide:

- **Colors:** Infra Navy `#0B1F3A`, Deep Blue `#12386B`, Signal Teal `#0F8B8D`, Amber `#F5A623`
- **Fonts:** Space Grotesk (headings), Inter (UI), JetBrains Mono (code)
- **Logo:** `assets/scaleplane_layered_planes.svg`

## Development

```bash
make setup      # Install all dependencies
make migrate    # Run Alembic migrations
make seed       # Seed demo data
make test-backend
```

### Auth note

JWT access tokens are stored in `localStorage` in the web UI for MVP simplicity. For production, prefer httpOnly cookies and refresh-token rotation.

### Multi-org extension

All resources are `organization_id`-scoped. The MVP uses a single default org; adding multi-org is a UI/header change, not a schema migration.

## License

Proprietary — see business plan for open-core strategy.

# rme-codex

Monorepo for the Rekam Medis Elektronik (RME) project.

## Getting Started

### 1. Run with Docker Compose

Environment defaults are provided in `backend/.env.example` and `frontend/.env.example`.

```bash
docker compose -f infra/docker-compose.yml up --build
```

Backend API: <http://localhost:8000>

Frontend app: <http://localhost:3000>

### 2. Health check

```bash
curl http://localhost:8000/api/healthz
```

Expected response:

```json
{"status": "ok"}
```

## Usage

### Seed demo tenants and users

```bash
cd backend
python manage.py migrate  # first time
python manage.py seed_demo
```

Creates:

- Tenant `system` with user `superadmin` / `password`
- Tenant `clinic` with user `clinicadmin` / `password`

### Obtain JWT tokens

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: <tenant_uuid>" \
  -d '{"username": "clinicadmin", "password": "password"}' \
  http://localhost:8000/api/auth/login/
```

### Authenticated request

```bash
curl -H "Authorization: Bearer <access_token>" \
  -H "X-Tenant-ID: <tenant_uuid>" \
  http://localhost:8000/api/users/
```

### Manage patients

```bash
curl -H "Authorization: Bearer <access_token>" \
  -H "X-Tenant-ID: <tenant_uuid>" \
  -d '{"full_name":"John","mrn":"001"}' \
  http://localhost:8000/api/patients/
```

List, search, and paginate:

```bash
curl -H "Authorization: Bearer <token>" \
  -H "X-Tenant-ID: <tenant_uuid>" \
  'http://localhost:8000/api/patients/?search=john&page=1'
```

## Development without Docker

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

OpenAPI schema is available at `/api/schema/` and interactive docs at `/api/docs/`.

### Update OpenAPI schema

```bash
cd backend
python manage.py spectacular --file schema.yaml
```

> When adding API views, include a `serializer_class` (or use `GenericAPIView`) so schema generation succeeds.

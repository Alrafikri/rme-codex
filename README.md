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

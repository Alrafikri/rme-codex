# rme-codex

This repository houses the monorepo for the Rekam Medis Elektronik (RME) project.

## Backend quickstart

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py runserver
```

### Health check

After the server is running, verify it with:

```bash
curl http://localhost:8000/api/healthz
```

The endpoint returns:

```json
{"ok": true}
```

The API schema is available at `/api/schema/` and interactive docs at `/api/docs/`.

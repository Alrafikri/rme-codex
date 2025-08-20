# AGENTS.md — Codex Guide for **RME (Rekam Medis Elektronik)**

> You are a senior full‑stack engineer agent. Build and maintain an MVP, cloud, **multi‑tenant** RME for Indonesian clinics. Optimize for **Build → Measure → Learn**. Keep changes shippable, documented, and testable.

---

## 0) Ground Rules

1. **Mobile‑first UX**: design, layout, and performance decisions prioritize phones.
2. **Multitenancy is non‑negotiable**:
   - Never trust client‑provided `tenant_id`. Derive from subdomain or `X-Tenant-ID` (dev only).
   - All domain tables have `tenant_id UUID NOT NULL`; enforce scoping server‑side.
3. **Stack**
   - Backend: **Django 5**, **DRF**, SimpleJWT; Postgres (Supabase) via `psycopg`.
   - Frontend: **Next.js 14 (App Router, TS)**, React Query, Tailwind + shadcn/ui, Zod.
   - Tooling: Docker Compose, Ruff+Black, mypy (lenient), ESLint+Prettier, Vitest/Playwright, Pytest.
4. **Compliance hooks**: prepare stubs for **SATUSEHAT** integration (OAuth2, Patient/Encounter upsert). Do **not** hard‑code secrets.
5. **OpenAPI always on**: DRF Spectacular exposes `/api/schema` and `/api/docs`.
6. **Observability**: log JSON to stdout incl. `tenant_id`, request id, latency. Add Sentry stubs.
7. **Security**: JWT access (5m) + refresh (30d, rotation). No secrets in repo. CORS only for known origins.
8. **PR hygiene**: small diffs, tests + linters green, update docs when behavior changes.

---

## 1) Repository Layout (monorepo)

```
rme/
  backend/
    manage.py
    rme_core/
    apps/
      tenants/            # subdomain → tenant resolver, base models, permissions
      users/
      patients/
      admissions/
      queue/
      outpatient/
      emr/
      billing/
      booking/
      reporting/
      integrations/satusehat/
    requirements/ or pyproject.toml
    docker/
  frontend/
    app/
      (auth)/
      (tenant)/
        dashboard/
        admissions/
        queue/
        visits/
        emr/
        billing/
      booking/            # public patient flow
    components/
    lib/
    docker/
  infra/
    docker-compose.yml
    k8s/                  # later
  docs/
```

---

## 2) Environment & Secrets

Create `.env` files (NEVER commit):

**Backend**

```
DATABASE_URL=postgresql://user:pass@host:5432/db
DJANGO_SECRET_KEY=...
ALLOWED_HOSTS=*
JWT_SIGNING_KEY=...
SATUSEHAT_BASE_URL=https://...
SATUSEHAT_CLIENT_ID=...
SATUSEHAT_CLIENT_SECRET=...
```

**Frontend**

```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
SENTRY_DSN=
```

Local dev may pass `X-Tenant-ID` header. Prod uses `{tenant}.app.domain` subdomains.

---

## 3) First‑Run / Dev Commands

> All commands are designed to run from repo root unless noted.

### 3.1 Docker up (local)

```bash
docker compose -f infra/docker-compose.yml up --build
```

Services: `backend`, `frontend`, `db` (local Postgres), optional `pgadmin`.

### 3.2 Backend (Django)

```bash
cd backend
# install deps (choose one)
pip install -r requirements.txt
# or
poetry install

python manage.py migrate
python manage.py createsuperuser  # for the first time
# Seed demo data (implements a custom mgmt cmd)
python manage.py seed_demo  # creates tenant "demo", admin, sample patients/visits

# Run API
authbind --deep python manage.py runserver 0.0.0.0:8000
# Health check
curl http://localhost:8000/api/healthz  # {"status":"ok"}
# OpenAPI (file export)
python manage.py spectacular --file schema.yaml
```

### 3.3 Frontend (Next.js)

```bash
cd frontend
pnpm install
pnpm dev  # http://localhost:3000
```

---

## 4) Data Model (MVP, all with `id UUID`, `tenant_id UUID`, `created_at/updated_at`)

- `tenant(id, name, subdomain)`
- `user(id, email, password_hash, full_name, role [ADMIN,DOCTOR,NURSE,STAFF,CASHIER], is_active, tenant_id)`
- `patient(id, mrn, nik, name, dob, sex, phone, address, bpjs_no, tenant_id)`
- `appointment(id, patient_id, provider_id, scheduled_at, status [BOOKED,CHECKED_IN,CANCELLED,NO_SHOW], reason, tenant_id)`
- `visit(id, patient_id, provider_id, started_at, ended_at, status [OPEN,CLOSED], visit_type [RAWAT_JALAN], triage_level, tenant_id)`
- `queue_ticket(id, visit_id, number, status [WAITING,IN_PROGRESS,DONE,SKIPPED], room, tenant_id)`
- `clinical_note(id, visit_id, soap_json, icd10_code, snomed_code, attachments[], author_id, signed_at, tenant_id)`
- `order(id, visit_id, type [LAB,RAD,PROCEDURE,DRUG], payload_json, status, tenant_id)`
- `invoice(id, visit_id, total, status [DRAFT,ISSUED,PAID,VOID], payer_type [CASH,BPJS], tenant_id)`
- `invoice_item(id, invoice_id, code, description, qty, unit_price, subtotal, tenant_id)`
- `payment(id, invoice_id, method [CASH,TRANSFER,EDC], amount, paid_at, ref_no, tenant_id)`
- `booking_token(id, patient_id, token, expires_at, used, tenant_id)`

Indexes: per table on `(tenant_id)` and on common access patterns (e.g. `(tenant_id, scheduled_at)`).

---

## 5) API Surface (DRF)

- **Auth**: `/api/auth/login` (JWT), `/api/auth/refresh`, `/api/auth/logout` (blacklist)
- **Patients**: CRUD
- **Admissions**: `POST /api/admissions/check-in` → create `visit` + `queue_ticket`
- **Queue**: `POST /api/queue/next` → atomically mark next WAITING → IN\_PROGRESS
- **Visits**: CRUD, `POST /api/visits/{id}/close` → compute invoice draft
- **EMR**: `clinical_notes` CRUD (SOAP: `{S,O,A,P}`), ICD‑10 picker from local JSON
- **Billing**: invoices, invoice items, payments
- **Booking**: `/api/appointments` CRUD + magic‑link/OTP stub
- **Exports**: `/api/exports/bpjs/patients.csv`, `/visits.csv`, `/invoice_lines.csv`
- **Docs**: `/api/docs` (Swagger/Redoc), `/api/schema`

All endpoints are **tenant‑scoped** via middleware + filter backend; ignore/override client `tenant_id`.

---

## 6) Frontend (Next.js App Router)

- **Auth** screens for staff, token refresh, role guard.
- **(tenant)/** pages use subdomain (dev: fallback header) to scope API calls.
- **Screens**
  - **Dashboard**: KPIs (today visits, waiting count, avg wait, revenue today), simple chart (7 days)
  - **Admisi**: register/search patient → check‑in (creates visit + queue ticket)
  - **Antrian**: live queue board; call next; mark done/skip
  - **Rawat Jalan / EMR**: visit list; visit detail with SOAP editor, ICD‑10 search, orders
  - **Kasir**: invoice view/edit; mark paid; CSV export area
  - **Booking Online (public)**: patient self‑booking, magic‑link/OTP stub

**UI**: Tailwind, shadcn/ui, optimistic React Query mutations, toasts for actions. Focus on fast forms & lists.

---

## 7) Multitenancy Mechanics

- **Middleware** `TenantFromHostMiddleware` resolves subdomain → `tenant_id` (cache 5 min). Dev override via `X-Tenant-ID`.
- **BaseModel** includes `tenant_id`; **QuerySet mixin** autopopulates filters.
- **DRF FilterBackend** enforces `tenant_id` scoping on all viewsets.
- All write serializers set `tenant_id` from request context; ignore incoming.

---

## 8) Testing, Linting, CI

### Python

```bash
pytest -q
ruff check backend
black --check backend
mypy backend --ignore-missing-imports
```

### JS/TS

```bash
pnpm lint
pnpm test
# e2e (once basic flows exist)
pnpm exec playwright test
```

### CI (GitHub Actions)

- Jobs: lint, typecheck, test, build Docker images. On `main`, build & push images.

---

## 9) Execution Plan (Agent Steps)

1. **Bootstrap**: monorepo, env files, Docker Compose, CI skeleton, `/api/healthz`.
2. **Tenants & Auth**: models, middleware, JWT, roles, seed superadmin + clinic admin.
3. **Patients**: CRUD + basic search & pagination.
4. **Admissions & Queue**: check‑in endpoint; queue state machine; live list.
5. **Visits & EMR**: SOAP editor (JSON), ICD‑10 lookup (local JSON), close visit → invoice draft.
6. **Billing**: invoices, items, payments; mark paid; totals.
7. **Dashboard & Exports**: KPIs + 3 CSV endpoints.
8. **Booking Online**: public routes; minimal OTP/magic‑link stub.
9. **SATUSEHAT stubs**: OAuth2 client; Patient/Encounter upsert methods; feature flag.
10. **Polish**: docs, seed data, basic metrics, small fixes.

Each step must ship with:

- Unit/integration tests for new logic
- Updated OpenAPI
- Minimal docs (README sections)

---

## 10) Definition of Done (per module)

- **Isolation**: all queries/creates are tenant‑scoped without trusting client `tenant_id`.
- **Auth**: roles enforced in DRF permissions (ADMIN/DOCTOR/NURSE/STAFF/CASHIER).
- **UX**: mobile‑first responsive pages; forms validate and toast errors/success.
- **Perf**: list endpoints paginated; N+1 avoided where obvious; useful indexes.
- **Docs**: `/api/docs` reflects reality; module README section updated.
- **Tests**: happy path + 1–2 edge cases (e.g., cross‑tenant access blocked).

---

## 11) Common Agent Tasks & Commands

### Scaffolding a new Django app

```bash
python manage.py startapp admissions apps/admissions
```

Wire in `INSTALLED_APPS`, urls, and add tests.

### Generating and running migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

> **Guard**: Any destructive migration requires env `ALLOW_DESTRUCTIVE_MIGRATIONS=true` and an approval comment in PR.

### Seeding demo data

```bash
python manage.py seed_demo --tenant demo --users --patients --visits
```

### Exporting CSVs (manual check)

```bash
curl -H "X-Tenant-ID: <uuid>" http://localhost:8000/api/exports/bpjs/patients.csv -o patients.csv
```

### Regenerating OpenAPI

```bash
python manage.py spectacular --file schema.yaml
```

---

## 12) Frontend Conventions

- Use **Server Components** for data fetch where possible; client components for forms.
- `lib/api.ts` centralizes fetcher (adds auth headers, `X-Tenant-ID` in dev).
- Zod schemas mirror backend serializers; narrow types at the boundary.
- React Query for mutations with optimistic updates and invalidation.
- Components in `components/ui/` prefer shadcn primitives.

---

## 13) SATUSEHAT (stubs)

- `integrations/satusehat/` contains:
  - OAuth2 client with token cache
  - Services: `upsert_patient()`, `upsert_encounter()`
  - `SATUSEHAT_ENABLED` feature flag; when false, functions no‑op and log.
  - Mock tests verify payload shape and error handling.

---

## 14) Smoke Test (Manual)

1. Login as clinic admin.
2. Create/search patient → **Check‑in**.
3. Verify patient appears in **Queue**; call **Next**.
4. Open **Visit**; add SOAP note with ICD‑10; close visit → invoice draft.
5. Open **Kasir**; add payment; mark invoice **Paid**.
6. Open **Dashboard**; see counts; download CSV exports.
7. Open public **Booking**; create appointment; see status in staff view.

---

## 15) Troubleshooting

- **401/403**: check JWT storage/refresh and role permissions.
- **Cross‑tenant data**: confirm middleware ran; ensure `TenantFilterBackend` enabled; serializers ignore `tenant_id` input.
- **CORS**: restrict to known frontend origins in settings.
- **Migrations fail**: ensure DB URL is valid; check privilege; re‑run `makemigrations`.

---

## 16) Coding Standards

- Python: Ruff/Black default; type hints on public functions; service layer for business rules.
- JS/TS: ESLint/Prettier; prefer explicit types; keep components small.
- Commits: Conventional Commits (`feat:`, `fix:`, `chore:`, `test:`...).

---

## 17) What to Build Next (Queue for Agent)

1. `feat(bootstrap):` healthcheck endpoint `/api/healthz` + CI skeleton.
2. `feat(tenants+auth):` models, middleware, JWT, roles, seed.
3. `feat(patients):` CRUD + search; mobile forms.
4. `feat(admissions+queue):` check‑in, state machine, live board.
5. `feat(visits+emr):` SOAP editor, ICD‑10 search, close visit → invoice.
6. `feat(billing):` invoice/items/payments; mark paid.
7. `feat(dashboard+exports):` KPIs + CSV endpoints.
8. `feat(booking):` patient booking flow (public) with magic‑link/OTP stub.
9. `feat(satusehat-stub):` OAuth2 client + upsert services + tests.
10. `chore:polish`: metrics, docs, seeds.

---

## 18) Agent Self‑Tests for **Measure** & **Acceptance**

> Codex must **implement** and **run** the checks below for each step. Use the exact file paths and Make targets so CI can gate merges.

### Global Conventions
- **Back‑end tests** live in `backend/apps/**/tests/` using `pytest` + DRF `APIClient`.
- **E2E tests** live in `frontend/tests/e2e/` using **Playwright**.
- **Smoke scripts** live in `scripts/smoke/*.sh` (curl‑based), runnable locally and in CI.
- **Make targets** expose one‑liners; CI calls these. Examples:
  ```bash
  make test            # all unit/integration tests
  make test:patients   # scoped to patients module
  make e2e             # all Playwright tests (headed in CI via xvfb)
  make e2e:patients
  make smoke:patients
  ```

### Reusable Test Template (per step)
For each Execution Plan step `N`, add a folder `docs/checklists/step-N/` that contains:
- `MEASURE.md`: bullets of measurable outcomes
- `ACCEPTANCE.md`: user‑observable acceptance checklist
- Link to corresponding tests and scripts

**Pytest structure template**
```python
# backend/apps/<module>/tests/test_stepN_measure.py
# backend/apps/<module>/tests/test_stepN_acceptance.py
```
**Playwright structure template**
```ts
// frontend/tests/e2e/stepN_<module>.spec.ts
```
**Smoke script**
```bash
# scripts/smoke/stepN_<module>.sh
```

---

### Agent Instruction (one‑liner to embed per step)
> - Always keep the app runnable and error-free after each PR and update this file when expectations change.
> - “After implementing Step **N**, create **pytest**, **Playwright**, and **smoke** checks matching the **Measure** and **Acceptance** bullets, expose them via `make test:<module>`, `make e2e:<module>`, `make smoke:<module>`, and **run them in CI**. Treat failures as blockers.”
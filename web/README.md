# Innohealth ThermalMesh -- Web Platform

A full-stack web application around the [ThermalMesh Python engine](../docs/architecture.md):
a public marketing site with an interactive 3D hero, an authenticated app for
uploading/processing/exploring thermal-mapped 3D reconstructions, and an
admin panel with real usage metrics, job monitoring, and audit logs.

> **Demo data.** Every account is seeded with 3 demo projects
> (`Thermal Scan Alpha/Beta/Gamma`). These are **not mock numbers** -- they
> are real synthetic datasets (known geometry, known analytic temperature
> field, ray-cast thermal images -- see [`../src/thermalmesh/synthetic.py`](../src/thermalmesh/synthetic.py))
> run through the actual pipeline at first startup. They are marked
> `is_demo: true` everywhere in the API/UI and must never be presented as
> real Innohealth measurements.

## Architecture

```
Next.js (React/TS, App Router)        FastAPI (Python)
  public site + 3D hero        <-->     /api/auth, /api/projects,
  authenticated app                     /api/admin
  admin panel                             |
                                           v
                                   ThermalMeshEngineAdapter
                                   (app/engine/real_engine.py)
                                           |
                                           v
                                   thermalmesh pipeline (../src)
                                   -- the SAME engine documented in
                                      ../docs/architecture.md, not a mock
                                           |
                                           v
                                   SQLite/Postgres + local file storage
```

The frontend never talks to the processing engine directly -- it calls the
FastAPI backend, which calls `ThermalMeshEngineAdapter` (`app/engine/adapter.py`).
Swapping the engine implementation (a remote worker, a different pipeline
version) means implementing that interface again; no router or frontend
code changes.

## Repository layout

```
web/
  backend/
    app/
      core/        config, database, security (JWT + PBKDF2 hashing),
                    storage abstraction, upload validation, auth deps
      models/       SQLAlchemy models (User, Project, ProjectFile,
                    ProcessingJob/Stage, Camera, ThermalImage,
                    ProcessingResult, Report, AuditLog)
      schemas/      Pydantic request/response schemas
      engine/       ThermalMeshEngineAdapter + the real, pipeline-backed
                    implementation, stage-name mapping, DB persistence
      routers/      auth, projects, admin REST endpoints
      seed.py       first-run demo data (see above)
      main.py       FastAPI app, CORS, startup hook
    requirements.txt
    .env.example
  frontend/
    src/
      app/          Next.js App Router pages (public site, (app) group,
                     admin group)
      components/
        ui/         design-system primitives (Radix + cva, shadcn-style)
        three/       ThermalMeshViewer and every 3D subcomponent
        marketing/   landing page sections
        layout/      nav, footer, app shell, admin shell
        projects/    per-project tab components
      lib/api/       typed API client (one file per resource)
      hooks/         React Query hooks, SSE processing stream, reduced-motion/WebGL checks
      types/         shared TypeScript types + enums (mirrors the backend)
    package.json
    .env.example
```

## Local development

Requires Python 3.11+ (same as the root project) and Node.js 18+.

### Backend

```bash
cd web/backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt        # also installs ../.. (the thermalmesh engine)
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

First startup creates the database tables and seeds demo data (runs the
real pipeline 3 times -- takes roughly a minute). Default accounts:

| Role  | Email                  | Password  |
|-------|------------------------|-----------|
| Admin | admin@innohealth.com   | admin123  |
| User  | demo@innohealth.com    | demo1234  |

These are demo-only credentials, intentionally documented here -- rotate
them (and set a real `JWT_SECRET`) before any non-local deployment.

### Frontend

```bash
cd web/frontend
npm install
cp .env.example .env.local
npm run dev
```

Visit `http://localhost:3000`. `next.config.mjs` rewrites `/api/*` to the
backend (`NEXT_PUBLIC_API_URL`, default `http://127.0.0.1:8000`), so the
browser only ever talks to one origin and CORS isn't a concern in dev.

### Production build

```bash
npm run build && npm start   # frontend
uvicorn app.main:app --host 0.0.0.0 --port 8000   # backend, behind a real ASGI server/proxy
```

## Environment variables

**Backend** (`web/backend/.env`, see `.env.example`):

| Variable | Purpose | Default |
|---|---|---|
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite:///./thermalmesh.db` |
| `JWT_SECRET` | HMAC key for access tokens | insecure dev default -- **change this** |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` |
| `JWT_EXPIRES_MINUTES` | Token lifetime | `1440` |
| `STORAGE_PATH` | Local filesystem root for uploads/outputs | `./storage` |
| `CORS_ORIGINS` | Comma-separated allowed browser origins | `http://localhost:3000` |
| `MAX_UPLOAD_MB` | Per-file upload limit | `512` |

`DATABASE_URL` can point at Postgres (`postgresql+psycopg2://...`) with no
code changes -- no Postgres-only column types are used.

**Frontend** (`web/frontend/.env.local`):

| Variable | Purpose | Default |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | Backend origin the dev-server rewrite proxies to | `http://127.0.0.1:8000` |

## Authentication & authorization

- JWT bearer tokens (`Authorization: Bearer <token>`), issued by
  `POST /api/auth/login`, verified server-side on every protected route.
- Passwords are hashed with PBKDF2-HMAC-SHA256 + per-user salt (stdlib
  only, no compiled dependency).
- Two roles: `USER` and `ADMIN`. `/api/admin/*` is gated by a
  `require_admin` dependency -- the frontend hiding the admin nav link is
  a convenience, **not** the security boundary.
- Two endpoints that browser APIs fetch directly and can't attach headers
  to (`GLTFLoader` for `model.glb`, `EventSource` for the processing
  stream) accept the token as a `?token=` query parameter instead via
  `get_current_user_via_header_or_query`.

## Processing pipeline integration

`app/engine/real_engine.py::RealThermalMeshEngine` runs
`thermalmesh.pipeline.runner.run_pipeline` in a background thread pool
(`concurrent.futures.ThreadPoolExecutor`), using `on_stage_start`/
`on_stage_complete` callbacks (added directly to the pipeline in
`../../src/thermalmesh/pipeline/pipeline.py`) to update `ProcessingJob`/
`ProcessingStage` rows in real time. The frontend's processing page
subscribes via Server-Sent Events (`/api/projects/{id}/processing/stream`,
falling back to polling if the connection drops).

The pipeline's 18 internal stage functions are grouped into the 10 public
stage names shown in the UI -- see `app/engine/stage_mapping.py` for the
exact mapping and `../docs/architecture.md` for why the grouping is
uneven (some public stages cover several internal ones).

This is a single-process worker pool, appropriate for local
development/demo use per the "don't overengineer" brief. For production
scale, replace `RealThermalMeshEngine`'s executor with a real queue
(Celery/RQ/Redis) behind the same `ThermalMeshEngineAdapter` interface --
no router or frontend changes required.

## Database schema (high level)

`User` --< `Project` --< `ProjectFile`
`Project` --< `ProcessingJob` --< `ProcessingStage`
`Project` --< `Camera` --< `ThermalImage`
`Project` -- `ProcessingResult` (1:1)
`Project` --< `Report`
`AuditLog` (references `User`, optionally `Project`)

Full field definitions are in `app/models/*.py`; `ProjectFileType`,
`ProjectStatus`, `JobStatus`, `ProcessingStageName`, `CameraPoseSource`,
`ReportType`, and `AuditAction` enums live in `app/models/enums.py` and are
mirrored in `web/frontend/src/types/enums.ts`.

## API reference

All routes are prefixed `/api`. Full request/response shapes are in
`app/schemas/*.py`; this is the endpoint list:

```
POST   /auth/login
POST   /auth/logout
GET    /auth/me
PATCH  /auth/me
POST   /auth/me/password
POST   /auth/request-access

GET    /projects
POST   /projects
GET    /projects/{id}
PUT    /projects/{id}
DELETE /projects/{id}

GET    /projects/{id}/files
POST   /projects/{id}/upload
DELETE /projects/{id}/files/{file_id}

POST   /projects/{id}/process
GET    /projects/{id}/processing
GET    /projects/{id}/processing/stream   (SSE)
POST   /projects/{id}/processing/cancel

GET    /projects/{id}/results
GET    /projects/{id}/model.glb
GET    /projects/{id}/thermal
GET    /projects/{id}/cameras
GET    /projects/{id}/temperature         (paginated, filterable)
GET    /projects/{id}/reports
GET    /projects/{id}/reports/{report_id}
GET    /projects/{id}/download/{artifact} (vertex_temperature | face_temperature | results_json | temperatures_csv)

GET    /admin/overview
GET    /admin/users
POST   /admin/users
PATCH  /admin/users/{id}
GET    /admin/projects
GET    /admin/jobs
GET    /admin/jobs/{id}
GET    /admin/audit
GET    /admin/system
GET    /admin/settings
```

Interactive Swagger docs are available at `http://localhost:8000/docs`
when the backend is running.

## 3D viewer notes

- `ThermalMeshViewer` loads the real per-project GLB (baked thermal
  texture from the pipeline) via `useGLTF`, with solid/wireframe/thermal/
  point-cloud/normals display modes, camera markers/frustums, a
  temperature legend, and click-to-inspect hotspots.
- **Hotspot picking** matches the clicked 3D point to the *nearest* row in
  the vertex temperature CSV by position, not by mesh index. This is
  deliberate: automatic UV unwrapping (`xatlas`) duplicates vertices along
  seams, so the GLB's vertex indices don't line up 1:1 with the original
  mesh's `vertex_id`s -- nearest-position matching sidesteps that safely
  since UV unwrapping never moves a vertex's position.
- **Camera-contribution toggling** (spec: enable/disable individual
  cameras and see the reconstruction update) is implemented as a
  visibility/frustum filter in the 3D scene and thermal-image browsing,
  not as live re-blending of the mesh -- that would require exposing the
  full per-image observation store (currently internal to the Python
  engine) and reimplementing weighted blending in the browser. Documented
  here rather than silently only doing half of it.
- Marketing-page 3D objects (hero, technology, showcase sections) use a
  procedural shader-based thermal gradient for visual effect only -- they
  are not derived from real temperature data and are not presented as
  such.

## Known limitations

- Next.js is pinned to `14.2.35` (patches the critical CVE from the
  original `14.2.15`); a handful of moderate/high-severity advisories
  remain in this line's transitive dependencies (see `npm audit`). A full
  Next 15 migration would resolve them but is out of scope for this demo
  platform per the "don't overengineer" brief.
- `/projects/{id}/temperature` loads the full `temperatures.csv` into
  memory per request before paginating -- fine at the demo scale this
  platform targets, not for meshes with millions of vertices.
- The processing "worker" is an in-process thread pool
  (`RealThermalMeshEngine`), not a distributed queue; see
  "Processing pipeline integration" above for the upgrade path.
- Job cancellation is best-effort: a queued job cancels cleanly, but a
  running job only stops at its next stage boundary (the pipeline itself
  has no finer-grained cancellation checkpoints).

## Testing this platform

There is no dedicated frontend/backend test suite yet (the underlying
`thermalmesh` engine has its own -- see `../tests/`). To verify the
platform manually: run both dev servers, log in as `demo@innohealth.com`,
open a seeded project, confirm the 3D viewer/cameras/temperature/reports
tabs load real data, then create a new project through the wizard with
your own PLY/thermal/camera files (or a synthetic set from
`thermalmesh generate-test-data`) and confirm processing completes and
produces a viewable model.

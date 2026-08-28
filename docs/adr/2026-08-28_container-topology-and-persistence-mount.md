# ADR-3: Container topology and persistence mount

**Date:** 2026-08-28  
**Project:** FoodFlow  
**Requested by:** human  
**Requirements:** `docs/requirements.md`  
**Implementation plan:** `docs/implementation-plan.md`  
**Status:** 🟡 pending approval  
**Supersedes:** N/A  
**Superseded by:** N/A

---

## Context

T-9 (`docs/implementation-plan.md:71-75`) adds the docker-compose deployment stack. The stack must deploy with a single command, expose the web interface on the local network, and persist the SQLite database across container recreation (`NFR-1`, `NFR-2`, `NFR-3`). The plan proposes `docker-compose.yml`, `backend/Dockerfile`, and `frontend/Dockerfile`, but the container topology (one service vs. two) and how the React build is served are architecture decisions. The homeserver has Docker and docker-compose with sufficient resources (`docs/requirements.md:156`); there is no scaling or multi-host need.

---

## Decision

We will use a single docker-compose service: the React app is built at image build time and served as static files by the FastAPI backend, and the SQLite database is persisted via a bind mount to a `./data` directory on the host.

---

## Options considered

### Option A — Single container: backend serves the built React app

The frontend is built during the Docker image build; the static build output is copied into the FastAPI image and served by FastAPI's `StaticFiles`. One service, one port.

**Pros:** One service to run and manage; one port to expose; no CORS in production (same origin); simplest compose file; smallest footprint on the homeserver.  
**Cons:** Frontend and backend share a lifecycle (rebuild the image to ship a frontend change); no independent scaling (not needed here).

### Option B — Two containers: backend + nginx serving the React app

A separate nginx (or similar) container serves the built React app and proxies `/api` to the backend container.

**Pros:** Clean separation of concerns; frontend and backend can be rebuilt independently; nginx is a battle-tested static server.  
**Cons:** Two services and two ports to manage; requires a reverse-proxy config; more moving parts than the scope needs; introduces CORS or proxy routing complexity.

### Option C — Two containers: backend + Vite dev server in production

Run the Vite dev server as the production frontend container.

**Pros:** No build step needed in the image.  
**Cons:** Serving a dev server in production is inefficient and not a supported production pattern; rejected outright.

---

## Recommendation

Option A — a single container where FastAPI serves the built React app. It is the simplest topology that satisfies `NFR-1` (single-command deploy), `NFR-2` (persistence), and `NFR-3` (local-network access), and it eliminates CORS in production by serving the SPA and API from the same origin. The homeserver has no scaling or independent-deployment need, so the coupling of a single container is an acceptable trade-off. It satisfies AC-1 end-to-end on the deployed stack.

---

## Implementation guidance

### Data model

No new data model. The SQLite database file is created by the backend at startup (see ADR-1) and persisted on the host.

### Interface contract

- The container exposes a single HTTP port (e.g., `8000`) on the host, reachable on the local network.
- `GET /` and static asset paths serve the built React SPA.
- API routes under `/recipes`, `/plans`, and `/shopping-list` are served by FastAPI from the same origin.

### File and folder structure

```text
foodflow/
  docker-compose.yml
  backend/
    Dockerfile          ← multi-stage: build frontend, then copy static build into FastAPI image
    app/
      main.py           ← mounts StaticFiles for the built SPA (see ADR-1)
  frontend/
    Dockerfile          ← build stage for the React app (used by backend/Dockerfile)
  data/                 ← host bind-mount directory for the SQLite file (gitignored)
```

### Naming conventions

- Compose service name: `foodflow`.
- Bind-mount path: `./data:/app/data` (host directory `./data` mounted at `/app/data` in the container).
- SQLite file: `/app/data/foodflow.db` inside the container.

### Guard rails for the developer

- Do not run the Vite dev server in production; the image must contain a production build served as static files.
- Do not expose more than one port; the SPA and API share a single origin.
- Do not store the SQLite file inside the container filesystem without a mount; it must survive container recreation (`NFR-2`).
- Do not add TLS/HTTPS, a reverse proxy, or external network exposure (out of scope, `docs/requirements.md:37-39`).
- Do not add authentication at the deployment layer (out of scope, `docs/requirements.md:32`).

---

## Acceptance criteria satisfied

- AC-1 → The single-container stack serves the full recipe CRUD flow end-to-end on the deployed stack.
- NFR-1 → One `docker-compose up` command deploys the stack and exposes the web interface.
- NFR-2 → The SQLite file lives on a bind mount and survives container recreation.
- NFR-3 → The single exposed port is reachable within the local network with no authentication.

---

## Consequences

**Easier:** Simplest possible deployment; one service, one port, no CORS in production; easy backup by copying the `./data` directory.  
**Harder:** Frontend and backend ship together in one image; a frontend-only change requires a full image rebuild.  
**Technical debt introduced:** None; the single-container coupling is a deliberate fit for the deployment context.

---

## Board updates

None — items affected by this ADR become eligible for `Ready` upon human approval; planning applies the transition.

---

**Approved by:** ________________  
**Approval date:** ________________  
**Next agent:** developer (+ tester in parallel)

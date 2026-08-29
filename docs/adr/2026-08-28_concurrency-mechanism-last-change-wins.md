# ADR-4: Concurrency mechanism (last change wins)

**Date:** 2026-08-28  
**Project:** FoodFlow  
**Requested by:** human  
**Requirements:** `docs/requirements.md`  
**Implementation plan:** `docs/implementation-plan.md`  
**Status:** ✅ approved  
**Supersedes:** N/A  
**Superseded by:** N/A

---

## Context

T-10 (`docs/implementation-plan.md:77-81`) hardens concurrent access. Two users access the same data simultaneously without authentication (`NFR-4`, `docs/requirements.md:91-92`). The human has decided the conflict-resolution strategy is **last change wins** (`docs/requirements.md:92,148-149`). The concrete mechanism — plain last-write-wins PUT/PATCH semantics with SQLite write serialization, or versioning with conflict rejection — is an architecture decision. The requirements state the need and the chosen strategy; the implementation detail is left to the architect.

---

## Decision

We will implement plain last-write-wins semantics: every write is a full or partial update that overwrites the current state, and SQLite serializes writes (WAL mode, transactions, busy timeout) so concurrent writes cannot corrupt data. No versioning and no conflict rejection.

---

## Options considered

### Option A — Plain last-write-wins with SQLite write serialization

Each PUT/PATCH overwrites the current row(s) in a transaction. SQLite is a single-writer database; WAL mode allows concurrent reads with a single writer, and a busy timeout makes concurrent writers wait rather than fail. The last committed write wins.

**Pros:** Matches the human's decision exactly; no conflict-rejection UX (no 409s); simplest mechanism; SQLite's single-writer model guarantees no corruption.  
**Cons:** A user's concurrent edit can be silently overwritten by another user's later write; no way to detect that a write was based on stale data.

### Option B — Optimistic locking with version numbers

Each resource carries a version; a write must present the current version or the server rejects it with `409 Conflict`.

**Pros:** Detects concurrent edits and prevents silent overwrites.  
**Cons:** Contradicts the human's "last change wins" decision — it rejects, rather than accepts, the last change; requires the frontend to handle conflict errors and retry; adds complexity. Rejected as contrary to the fixed decision.

### Option C — Real-time sync (WebSockets / CRDT)

Keep clients in sync in real time and merge concurrent edits.

**Pros:** No lost updates; live multi-user experience.  
**Cons:** Far beyond the scope; requires a WebSocket layer and merge logic; contradicts the simple "last change wins" decision. Rejected as scope creep.

---

## Recommendation

Option A — plain last-write-wins with SQLite write serialization. It is the only option that honors the human's fixed decision (`docs/requirements.md:92`) while guaranteeing no data corruption, which is what `NFR-4` and AC-5 actually require. SQLite's single-writer model with WAL mode and a busy timeout provides the write serialization for free, with no versioning or conflict-handling code in the frontend. It satisfies AC-5 (both users see the new recipe after refresh; no data lost or corrupted).

---

## Implementation guidance

### Data model

No new columns or tables. Concurrency is handled at the database and transaction layer, not in the schema.

### Interface contract

- All write endpoints (`POST`/`PATCH`/`DELETE` on recipes and plans) run inside a single SQLAlchemy transaction that commits atomically.
- SQLite is opened with WAL mode (`PRAGMA journal_mode=WAL`) and a busy timeout (e.g., `PRAGMA busy_timeout=5000`).
- Reads use the same connection pool; WAL allows concurrent readers with a single writer.
- No endpoint returns a conflict error; the last committed write is the final state.

### File and folder structure

No new files. Changes are confined to the existing backend files from ADR-1:

```text
foodflow/
  backend/app/
    db.py              ← enable WAL mode and busy_timeout on engine creation
    routes/recipes.py  ← wrap writes in transactions (T-2)
    routes/plans.py    ← wrap writes in transactions (T-3)
```

### Naming conventions

No new naming conventions; follow ADR-1.

### Guard rails for the developer

- Do not add version columns, ETags, or `409 Conflict` handling; the decision is last-write-wins, not optimistic locking.
- Do not add WebSockets, real-time sync, or CRDT logic (out of scope).
- Do not disable SQLite's write serialization or use `PRAGMA journal_mode=OFF`; WAL mode is required.
- Do not add authentication or per-user data isolation (out of scope, `docs/requirements.md:32,35`).
- Do not implement client-side merge or conflict UI; the frontend simply refetches on refresh (T-5 API client).

---

## Acceptance criteria satisfied

- AC-5 → WAL mode + single-writer serialization ensures two users can view and modify the same data without corruption; both see the new recipe after their view refreshes, and no data is lost or corrupted.
- NFR-4 → The mechanism implements the human's "last change wins" strategy for concurrent recipe and plan edits.

---

## Consequences

**Easier:** No versioning, no conflict handling, no frontend retry logic; SQLite provides serialization for free.  
**Harder:** A user's concurrent edit can be silently overwritten by a later write; there is no mechanism to surface that an edit was based on stale data.  
**Technical debt introduced:** None; the silent-overwrite behavior is the accepted consequence of the human's explicit decision.

---

## Board updates

None — items affected by this ADR become eligible for `Ready` upon human approval; planning applies the transition.

---

**Approved by:** human  
**Approval date:** 2026-08-28  
**Next agent:** developer (+ tester in parallel)

# ADR-7: Backend HTTP client for Gemini API calls

**Date:** 2026-09-14  
**Project:** FoodFlow  
**Requested by:** human  
**Requirements:** `docs/requirements-ai-suggestions.md`  
**Implementation plan:** `docs/implementation-plan-ai-suggestions.md`  
**Status:** ✅ approved (2026-09-14)  
**Supersedes:** N/A  
**Superseded by:** N/A

---

## Context

T-1 (`docs/implementation-plan-ai-suggestions.md:23-27`) is marked **[requires architecture]**: the backend needs a new dependency to make HTTP requests to the Google AI Studio (Gemini) API. The backend currently has no HTTP client — `backend/requirements.txt` contains only `fastapi==0.115.6`, `uvicorn[standard]==0.34.0`, and `SQLAlchemy==2.0.36`. The requirements mandate a new dependency (`docs/requirements-ai-suggestions.md:139`); the specific library is an architecture decision. The endpoint must call the Gemini API synchronously (NFR-4: existing route functions are sync per `backend/app/routes/recipes.py`), handle all failure modes — network error, invalid API key, rate limit, non-200 response, and malformed body — and return HTTP 502 on any Gemini failure (FR-4, AC-4). The project pins exact versions in `requirements.txt` and follows a minimalist dependency philosophy (ADR-1, ADR-2, ADR-3 guard rails).

---

## Decision

We will use **httpx** (sync mode) as the HTTP client library in the backend to call the Google AI Studio (Gemini) API, pinned at version 0.28.1 in `backend/requirements.txt`.

---

## Options considered

### Option A — httpx (sync mode)

A modern, fully-featured HTTP client for Python with both sync and async APIs. We would use only the synchronous `httpx.Client` to align with the existing sync route pattern (NFR-4).

**Pros:** Modern design with explicit timeout and error handling; `httpx.HTTPStatusError` and typed exceptions (`httpx.ConnectError`, `httpx.TimeoutException`) simplify the FR-4 error handling; sync mode is a first-class citizen, not a wrapper; `client.post().raise_for_status()` gives clean non-200 detection; no dependency on `urllib3` internals; 5 direct dependencies (`httpcore`, `h11`, `certifi`, `idna`, `sniffio`) — lightweight; actively maintained (130M weekly downloads).  
**Cons:** Not yet at 1.0 stable (latest release 0.28.1); slightly less ubiquitous than `requests` in legacy projects.

### Option B — requests

The classic, battle-tested Python HTTP library with a sync-only API. Widely used (300M+ weekly downloads, 4M+ dependent repos).

**Pros:** Maximum stability and ecosystem maturity (v2.34.2, May 2026); very low risk; synchronous API is the only mode — no temptation to introduce async patterns; minimal dependency footprint.  
**Cons:** Wrapped around `urllib3` and carries its transitive dependency chain; error handling relies on `requests.exceptions.HTTPError` which is less granular than httpx's typed exceptions; no native async support if the project ever migrates routes to async (not needed now, but httpx costs nothing extra for future-proofing); the API surface is older and less explicit about timeouts and error semantics.

### Option C — google-genai SDK (`google-genai`)

The official Google Gen AI Python SDK (v2.20.0, Aug 2026). Provides a high-level `client.models.generate_content()` interface that abstracts the raw HTTP call and JSON parsing.

**Pros:** Official SDK maintained by Google; higher-level API handles prompt formatting, model selection, and response parsing; no need to construct raw HTTP requests or parse raw JSON.  
**Cons:** Heavyweight: 793 KB wheel with 18 transitive dependencies (including `google-auth`, `google-api-core`, `proto-plus`, `protobuf`, and more); violates the project's minimalist dependency philosophy (ADR-1, ADR-2, ADR-3 guard rails); opaque error handling — SDK exceptions wrap HTTP errors, making it harder to map to the specific FR-4 failure categories (network, invalid key, rate limit, non-200, malformed body); overkill for a single `POST` request that returns a JSON array; tightly coupled to Google's SDK versioning and breaking-change cadence.

---

## Recommendation

Option A — httpx (sync mode, pinned at 0.28.1). It is the best fit for this project's constraints: it provides a modern, explicit synchronous API that aligns with the existing sync route pattern (NFR-4), has a small dependency footprint (5 direct dependencies vs. requests' `urllib3` chain or google-genai's 18), and offers typed exceptions that directly map to the FR-4 error categories (network → `httpx.ConnectError`, timeout → `httpx.TimeoutException`, non-200 → `httpx.HTTPStatusError`, malformed body → `json.JSONDecodeError`). It satisfies AC-4 (the endpoint returns HTTP 502 on any Gemini failure) with clean, testable error handling. The 0.x version is acceptable because httpx has been stable since 0.23+ and the project pins exact versions. This introduces a new dependency to `backend/requirements.txt` [requires human approval].

---

## Implementation guidance

### Dependency change

Add to `backend/requirements.txt`:

```
httpx==0.28.1
```

This is the only change to `requirements.txt`. The five transitive dependencies (`httpcore`, `h11`, `certifi`, `idna`, `sniffio`) are installed automatically.

### Usage pattern

The endpoint uses `httpx.Client` in synchronous mode within the existing route function:

```python
import httpx

client = httpx.Client(timeout=30.0)
response = client.post(
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent",
    json={...},
    headers={"x-goog-api-key": api_key},
)
response.raise_for_status()
```

### Error handling contract

The endpoint catches the following and returns HTTP 502 with detail `"Failed to get AI suggestions"` (FR-4):

| Failure | httpx exception | Action |
|---|---|---|
| Network error (DNS, connection refused) | `httpx.ConnectError` | Return 502 |
| Timeout | `httpx.TimeoutException` | Return 502 |
| Non-200 response (401, 429, 500, etc.) | `httpx.HTTPStatusError` (from `raise_for_status()`) | Return 502 |
| Malformed response body (not valid JSON, unexpected shape) | `json.JSONDecodeError`, `KeyError`, `TypeError` | Return 502 |

All exceptions are caught in a single `except (httpx.HTTPError, json.JSONDecodeError, KeyError, TypeError)` block. The `GOOGLE_API_KEY` missing/empty check (FR-2) happens **before** the httpx call and returns HTTP 503 — it does not go through the error handler above.

### Prompt construction

Build the Gemini API request body as:

```json
{
  "contents": [{"parts": [{"text": "<prompt>"}]}],
  "generationConfig": {
    "responseMimeType": "application/json",
    "responseSchema": {
      "type": "ARRAY",
      "items": {"type": "STRING"}
    }
  }
}
```

The `<prompt>` includes the recipe name, the requested output language, and an instruction to return ingredient names only. Using `responseMimeType` and `responseSchema` ensures Gemini returns a valid JSON array of strings, reducing parse errors.

### File and folder structure

No new files are created. Changes to existing files:

| File | Change |
|---|---|
| `backend/requirements.txt` | Add `httpx==0.28.1` |
| `backend/app/routes/recipes.py` | Add `POST /recipes/suggest-ingredients` endpoint using `httpx.Client` |
| `backend/app/schemas.py` | Add `SuggestIngredientsRequest` and `SuggestIngredientsResponse` Pydantic schemas |

### Naming conventions

- Pydantic schemas: `SuggestIngredientsRequest` (input), `SuggestIngredientsResponse` (output) — follows the existing `*Request`/`*Read` pattern in `schemas.py`.
- Endpoint: `POST /recipes/suggest-ingredients` — added to the existing `router` in `recipes.py`.

### Guard rails for the developer

- Do not use `httpx.AsyncClient` or `async def` in route functions; the backend uses sync routes per NFR-4 (ADR-1, ADR-2 patterns).
- Do not implement retry logic, circuit breakers, or connection pooling across requests; a single `httpx.Client` per request is sufficient for this scale.
- Do not import or use `google-genai`, `google-generativeai`, or any Google SDK; the Gemini API is called via raw HTTP with httpx.
- Do not stream the Gemini response; use a single `client.post()` call that returns the complete response.
- Do not store the `httpx.Client` instance as a module-level or global variable; create it within the endpoint function for simplicity and isolation.
- Do not expose the raw Gemini error details to the frontend; always return the fixed detail strings defined by FR-2 and FR-4.

---

## Acceptance criteria satisfied

- **AC-3** → The httpx call is gated behind the `GOOGLE_API_KEY` check (FR-2); if the key is missing, the endpoint returns 503 before any httpx client is created.
- **AC-4** → httpx's typed exceptions (`ConnectError`, `TimeoutException`, `HTTPStatusError`) and Python's `json.JSONDecodeError` are caught and mapped to HTTP 502 with detail `"Failed to get AI suggestions"`, satisfying the error handling contract for invalid key, rate limit, network error, non-200, and malformed body.

---

## Consequences

**Easier:** Clean, typed error handling for all Gemini failure modes; small dependency footprint; sync mode aligns with existing code patterns; straightforward testing with `httpx` mocks.  
**Harder:** One additional dependency in `requirements.txt` (justified by the HTTP client requirement); the 0.x version number may cause concern (mitigated by exact pinning and httpx's proven stability since 0.23).  
**Technical debt introduced:** None. httpx is a widely-adopted, actively-maintained library. The 0.x version will reach 1.0 in the future, but the exact pin protects against breaking changes.

---

## Board updates

None — items affected by this ADR become eligible for `Ready` upon human approval; planning applies the transition.

---

**Approved by:** human  
**Approval date:** 2026-09-14  
**Next agent:** developer (+ tester in parallel)

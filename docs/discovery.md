# Discovery: FoodFlow

**Date:** 2026-08-28  
**Project:** FoodFlow  
**Requested by:** human  
**Status:** ✅ approved

---

## Problem statement

Planning weekly meals and knowing what to buy is a manual, repetitive process: the user must review recipes, decide the menu, and figure out the ingredients to purchase. The underlying problem is reducing that friction by letting the user register recipes once, build a flexible meal plan, and get an automatic shopping list derived from the plan.

---

## Goals

1. Allow the user to build a reusable recipe base by registering recipes (name and ingredient names only, no quantities).
2. Allow the user to plan meals over a flexible number of days (n), selecting any number of recipes (m ≥ n) from their recipe base, accommodating multiple meals per day.
3. Automatically generate a shopping list by aggregating ingredient names from all recipes in the current meal plan, with duplicates combined into a single list.
4. Enable two people (the user and their spouse) to use the app concurrently with shared access to the same recipe base and the same meal plan, without requiring authentication or accounts.
5. Run the application as a Docker container on the user's homeserver, accessible within their local network.

---

## Non-goals

- User authentication, accounts, or access control.
- Ingredient quantities, units, or measurements — the shopping list is a flat list of ingredient names only.
- Rich recipe metadata: categories, photos, preparation times, step-by-step instructions, nutritional information.
- Multi-user data isolation or per-user profiles.
- Integration with stores, pricing, or online shopping.
- Native mobile application.

---

## Assumptions

- The project is greenfield: no source code, architecture decisions, or prior artifacts exist yet.
- The user's homeserver runs Docker and has sufficient resources to host a Python backend + React frontend container setup.
- The app will be accessed within the local network; no external access, TLS termination, or proxy configuration is required.
- The shopping list aggregates ingredient names from all planned recipes, combining duplicates into a single list (i.e., if two recipes use "onion", the list shows "onion" once).
- The meal plan model is "in the next n days I will cook these m recipes" — it is not a day-by-day slot assignment. m ≥ n because multiple meals per day are allowed (breakfast + dinner, etc.).
- Two people will access the app simultaneously with no login; the data is fully shared between them. The concurrency model must handle this (e.g., no conflicting simultaneous edits on the same recipe or plan).
- The human's spouse is a second simultaneous user, not a separate account holder.

---

## Open questions

1. (Resolved) **Ingredient quantities?** — No. Ingredients are name-only. The shopping list is a flat list of ingredient names.
2. (Resolved) **Plan model?** — Flexible: the user defines n days and selects m recipes (m ≥ n). No rigid day-by-day slot assignment.
3. (Resolved) **Single user or multi-user with accounts?** — No accounts. Two people share the same data simultaneously. Concurrent access without authentication.
4. **How should concurrent edits be handled?** — Two users may try to edit the same recipe or meal plan at the same time. The technical approach (optimistic locking, last-write-wins, real-time sync, or simply accepting brief conflicts) is an architecture decision, but the discovery phase should note this as a design input.
5. **Database persistence model?** — The app needs persistent storage. SQLite is the simplest option for a single-container homeserver deployment, but this is an architecture decision. Noted here as a constraint to be resolved upstream of implementation.

---

## Constraints

- Backend in Python (declared by the human).
- Frontend in React (declared by the human).
- Must run as a Docker container on the user's homeserver (declared by the human).
- Project type: webapp (`conductor.yaml:8`).
- No authentication system — the app is open to anyone on the local network who can reach it.
- The data model has no concept of users or user-owned resources; everything is shared.

---

## Initial risks

- Concurrent shared access without conflict resolution → if two users edit the same recipe or plan simultaneously without any safeguard, data corruption or confusing UX may result.
- Homeserver environment unknown (architecture, resources, existing Docker setup, network topology) → deployment assumptions may not hold.
- Stack declared broadly (Python/React) with no framework choices yet → technical scope remains open until the architecture phase.
- No authentication on a local network → if the network is not fully trusted (e.g., guests, IoT devices), anyone can modify recipes and plans. This is an accepted trade-off unless the human decides otherwise.

---

## Existing context

- `README.md:3` — project description: "Plan your weekly meals and groseries" (contains typo "groseries").
- `conductor.yaml` — project config: name, slug, type webapp, GitHub Projects enabled (project #2, owner `sergiogg94`).
- `docs/` — only framework scaffolds (`architecture.md`, `requirements.md`, `delivery-checklist.md`, `discovery.md`); no real content.
- No source code, `AGENT_LOG.md`, or ADRs exist yet.

---

## Linked references

- Human's original request (verbatim, in the discovery conversation).
- `README.md`
- `conductor.yaml`

---

## Board updates

None — planning owns item creation.

Per the Conductor framework policy, `planner` is the only agent authorized to create items on the board. Discovery does not suggest board operations unless the human explicitly requests it.

---

**Approved by:** human  
**Approval date:** 2026-08-28  
**Next agent:** scopper

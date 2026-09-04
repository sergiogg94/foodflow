# AGENT_LOG

Decision and outcome log for FoodFlow, maintained by the orchestrator. Read before producing any artifact (core-principles §4).

---

## 2026-09-04 — Frontend language switch (session)

### Decisions

- **D-1 — New feature: frontend language switch.** Human request (verbatim): "Quiero agregar la funcionalidad de poder cambiar el idioma del frontend a español". Discovery interpretation confirmed by the human: **(a) a language selector English ↔ Spanish**. The choice persists **per device** (browser/device). **Default language: English**. Artifact: `docs/discovery-language-switch.md`.
- **D-2 — Session language policy.** All files generated in this session within the repo will be written in **English**, even though the conversation with the human is in Spanish. Human decision; overrides core-principles §11 for this session.
- **D-3 — AGENT_LOG.md created.** Human requested this file to record decisions taken. It was previously absent from the repository (noted in `docs/delivery-checklist.md:79`).

### Outcomes

- `docs/discovery-language-switch.md` updated: translated to English (per D-2), open questions resolved per D-1 (option (a), per-device persistence, English default). New assumption recorded: per-device persistence means local browser storage, not cross-device sync.
- `docs/discovery-language-switch.md` — ✅ approved by human (2026-09-04).
- `docs/requirements-language-switch.md` — created by scopper (English, 🟡 pending approval). 5 FR, 3 NFR, 6 AC, 8 edge cases, no open questions. Scoping choice flagged: selector placed in the app header (`frontend/src/App.tsx:19-32`).
- `AGENT_LOG.md` created at repo root (D-3).

### Pipeline state

- Stage: scopper (new feature).
- `docs/requirements-language-switch.md` — 🟡 pending human approval.
- Previous delivery (T-1..T-10): merged to `main`; `docs/delivery-checklist.md` 🟡 pending human acceptance (independent of this feature).
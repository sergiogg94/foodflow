---
description: Documentation stage - two modes: maintain README and docs aligned with implemented reality, or compile the delivery checklist consolidating requirements, tests, and review status for human acceptance.
agent: documenter
---

Run one Documentation cycle.

Mode and target (optional): $ARGUMENTS
- If the human asks for delivery closure or gives no mode, produce `docs/delivery-checklist.md` following your delivery checklist requirements: all four upstream artifacts must exist and be approved, otherwise stop and say what is missing.
- If the human names documentation to create or update, run documentation maintenance instead.

Follow your complete role definition, produce exactly one output per run, then stop and present it for human acceptance.

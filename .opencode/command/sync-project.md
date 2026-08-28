---
description: Board synchronization - compares GitHub Projects state against repository reality and emits suggested item operations (create, move, update) with evidence. Suggestions only; the human applies them.
agent: planner
---

Run one Project synchronization pass.

Scope filter from the human (optional): $ARGUMENTS

Follow the interaction rules of github-projects-policy.md. Read the current artifacts and repository state, compare them against what the board should reflect, and emit a reconciliation report listing every suggested operation (create / move / update) with its justification evidence. Do not mutate anything directly - the human applies the suggestions.

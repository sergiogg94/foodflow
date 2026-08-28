# GitHub Projects Policy

## Purpose

This document defines how Conductor agents interact with GitHub Projects so that the board always reflects the real state of work.

Its goals are to:

- connect planning artifacts to trackable work items
- prevent inconsistent board state when multiple agents operate on the same project
- make clear which agent may create, move, or update what — and under which conditions
- keep the human in control of the transitions that matter

This policy binds every agent, including future ones. Agent-specific prompts may narrow these rules but never widen them.

---

## Source of Truth

Each consumer repository defines its own board configuration in `conductor.yaml` under `github.projects`. That file wins over this document whenever values differ (field names, state names, project number).

What this document fixes are the **rules of interaction**, not the specific labels.

---

## Principles

1. **The board mirrors reality.** An item's state describes what has actually happened (approved, implemented, reviewed), never what an agent intends to do next.
2. **One item, one unit of work.** Each issue/board item maps to one task small enough to be implemented and reviewed in one pass, and traceable to its upstream artifact (scope brief, ADR).
3. **Transitions carry evidence.** No status change without a link to what justifies it: the PR, the review report, the test report, or the human's approval.
4. **Done belongs to the human.** No agent ever closes the loop on its own work.
5. **Silence is not consent.** If approval for a transition is missing, the item stays where it is.

---

## Default Board States

| State | Meaning |
|---|---|
| `Backlog` | Captured as work, but not yet scoped or planned |
| `Ready` | Scope brief and ADR approved; safe to implement |
| `In Progress` | A developer agent is actively working on it |
| `Review` | PR is open; awaiting review and human decision |
| `Blocked` | Waiting on a decision, input, or fix outside the current role |
| `Done` | Merged and accepted by the human |

---

## Fields

Required for the MVP:

- **Status** — one of the six states above.
- **Linked PR** — set when the pull request opening the work exists.
- **Type** — `Feature`, `Bug`, `Chore`, `Spike` (matches the issue templates).

Recommended:

- **Priority** — `P0` (critical) · `P1` (high) · `P2` (normal) · `P3` (low).
- **Effort** — `XS` · `S` · `M` · `L`.

Optional:

- **Area**, **Iteration**, **Risk** — use only if the project actually maintains them. Do not create structure nobody reads.

Avoid product-management ceremony beyond these fields. This framework serves individual developers directing agents, not reporting lines.

---

## Role Permissions

| Agent | May create items | May change Status | Notes |
|---|---|---|---|
| `planner` | **Yes — the only one** | Yes: `Backlog → Ready` | Also sets Type, Priority, Effort, links upstream artifacts |
| `developer` | No | Yes: `Ready → In Progress → Review` | Must set **Linked PR** when moving to `Review` |
| `tester` | No | No | Produces the test report consumed at `Review` |
| `reviewer` | No | Recommend only | Suggests return to `In Progress` on 🔄; never sets `Done` |
| `devops` | No | Only on CI/automation items | Same limits as `developer` for those items |
| `documenter` | No | No | Documentation updates never move the board |
| `orchestrator` | No | Validates and reports | Flags illegal transitions and stale items; mutates only if the human instructs it |
| Human | Anywhere | Anywhere | Sole owner of `Done`, `Blocked` resolution, and priority changes |

Anything not granted is forbidden. If an agent believes a transition is needed but lacks permission, it states this in its output instead of touching the board.

---

## Allowed Transitions

```
Backlog  →  Ready         planner, after human-approved scope brief + ADR(s)
Ready    →  In Progress   developer, when starting implementation
In Progress → Review      developer, when PR is open AND tests have run
Review   →  Done          HUMAN ONLY, after ✅ Approved review + acceptance
Review   →  In Progress   developer, after addressing 🔄 findings
Any      →  Blocked       any agent, with a comment naming what is missing
Blocked  →  prior state   whoever resolved the blocker, or the human
```

Forbidden regardless of role:

- skipping states (`Ready → Review`, `In Progress → Done`)
- returning to `Ready` once implementation started (split or re-plan instead)
- `Done` without an approved review and human acceptance

---

## Transition Discipline

Every status change must include, in the item or issue comments:

1. **What changed** — old state → new state.
2. **Why** — one sentence.
3. **Evidence** — PR link, report path (`docs/reviews/…`, `docs/tests/…`), or the human's approval.

Moving an item to `Blocked` additionally requires:

- what exactly is missing,
- who is expected to resolve it (role or human),
- the item it depends on, if applicable.

Stale items (e.g. `In Progress` with no activity across sessions) are flagged to the human, not silently updated.

---

## Done Criteria

An item may be marked `Done` only when all of the following hold:

- [ ] Review verdict is ✅ Approved
- [ ] All 🔴 blocking findings resolved
- [ ] Tests pass and acceptance criteria are verified
- [ ] Documentation affected by the change is updated
- [ ] The human has explicitly accepted the delivery checklist

---

## Conflicts and Escalation

- Two agents disagreeing about a state → the conservative state wins (the earlier one) and the conflict is escalated to the human.
- A required transition that no agent has permission to execute → requested in the relevant artifact or comment; never performed silently.
- Contradictions between this policy and `conductor.yaml` labels → follow `conductor.yaml` names, apply this policy's rules.

---

## MVP Mode (No Live Integration Yet)

Until the GitHub MCP integration is implemented, agents do not write to the board directly. Instead, each artifact ends with a short **Board Updates** section listing suggested operations:

```md
## Board Updates
- Move #12 Ready → In Progress (starting implementation)
- Set #12 Linked PR: <url>
```

The human applies them manually or via script. The rules in this document (permissions, evidence, forbidden transitions) apply to those suggestions exactly as they will apply to automated writes later.

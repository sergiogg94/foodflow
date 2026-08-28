# Implementation plan: {{FEATURE_NAME}}

**Date:** {{YYYY-MM-DD}}  
**Project:** {{PROJECT_NAME}}  
**Requested by:** human  
**Requirements:** `docs/requirements.md`  
**Status:** 🟡 pending approval

---

## Planning summary

<!--
One short paragraph. How the work was sliced and why: the strategy of the plan in plain words.
Reference the scope summary from the requirements artifact. No architecture decisions here.
-->

{{PLANNING_SUMMARY}}

---

## Task breakdown

<!--
Stable identifiers T-1, T-2, ... Each task:
- traces to at least one FR and one AC from the requirements
- is small enough to be implemented and reviewed in one pass
- names real files or folders affected, when known
Mark tasks that cannot be defined without a technical decision as: [requires architecture].
-->

### T-1 — {{TASK_TITLE}}

**Traces to:** FR-N, AC-N  
**Touches:** {{PATHS}}  
{{TASK_DESCRIPTION}}

### T-2 — {{TASK_TITLE}}

**Traces to:** FR-N, AC-N  
**Touches:** {{PATHS}}  
{{TASK_DESCRIPTION}}

---

## Suggested issue structure

<!--
One block per task. Title format: "T-N <imperative title>".
Type is one of: Feature, Bug, Chore, Spike.
The issue body should reference the FRs and ACs the task satisfies.
-->

| Task | Issue title | Type |
|---|---|---|
| T-1 | {{ISSUE_TITLE}} | Feature |
| T-2 | {{ISSUE_TITLE}} | Chore |

Issue body outline for each: purpose (1 line), requirements covered (FR-N list), acceptance criteria to verify (AC-N list), files affected.

---

## Priority order

<!--
Ordered list with justification. P0 = critical for end-to-end use case, P1 high, P2 normal, P3 low.
Justify by criticality to the main use case, not by convenience.
-->

1. **P0** — {{TASKS_AND_WHY}}
2. **P1** — {{TASKS_AND_WHY}}
3. **P2** — {{TASKS_AND_WHY}}

---

## Dependencies and blockers

<!--
Only genuine blockers between tasks, not convenience ordering.
Format: T-N depends on T-M because [reason].
If there are none, write "None."
-->

- T-1 → depends on T-2 because {{REASON}}

---

## GitHub Projects mapping

<!--
Initial field values per item. Items start in Backlog:
moving to Ready requires approved architecture, which does not exist yet at planning time.
-->

| Task | Status | Priority | Effort |
|---|---|---|---|
| T-1 | Backlog | P0 | {{XS/S/M/L}} |
| T-2 | Backlog | P1 | {{XS/S/M/L}} |

---

## Suggested execution sequence

<!--
Ordered steps for execution. Group tasks that can run in parallel.
Note which stages come after planning: architect first, then developer + tester per pipeline.
-->

1. {{FIRST}} 
2. Then in parallel: {{PARALLEL_TASKS}}
3. Finally: {{LAST}}

---

## Board updates

<!--
Exact operations for the human to apply, one per line. Planner suggests; never executes.
Per github-projects-policy.md only planner may propose creating items.
-->

```text
Create issue "T-1 {{ISSUE_TITLE}}" (type: Feature), add to project {{PROJECT_NUMBER}}, set Priority P0, set Effort M, set Status Backlog
Create issue "T-2 {{ISSUE_TITLE}}" (type: Chore), add to project {{PROJECT_NUMBER}}, set Priority P1, set Effort XS, set Status Backlog
```

---

**Approved by:** ________________  
**Approval date:** ________________  
**Next agent:** architect

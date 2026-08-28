# ADR-{{NUMBER}}: {{DECISION_TITLE}}

**Date:** {{YYYY-MM-DD}}  
**Project:** {{PROJECT_NAME}}  
**Requested by:** human  
**Requirements:** `docs/requirements.md`  
**Implementation plan:** `docs/implementation-plan.md`  
**Status:** 🟡 pending approval  
**Supersedes:** {{ADR-NUMBER or "N/A"}}  
**Superseded by:** N/A

---

## Context

<!--
One short paragraph. Describe the situation that makes this decision necessary.
Reference the requirements and the plan task(s) this decision unblocks ([requires architecture] markers).
State the constraints that narrow the options: stack, scale, existing ADRs.
Do not describe the decision itself here.
-->

{{CONTEXT}}

---

## Decision

<!--
One sentence. State clearly what has been decided.
Format: "We will use [X] for [Y]."
-->

{{DECISION_STATEMENT}}

---

## Options considered

<!--
2-3 genuinely viable alternatives. No strawmen. Concrete advantages and disadvantages
in THIS project's context, not generic ones.
Remove Option C if only two are viable.
-->

### Option A — {{OPTION_A_NAME}}

{{OPTION_A_DESCRIPTION}}

**Pros:** {{OPTION_A_PROS}}  
**Cons:** {{OPTION_A_CONS}}

### Option B — {{OPTION_B_NAME}}

{{OPTION_B_DESCRIPTION}}

**Pros:** {{OPTION_B_PROS}}  
**Cons:** {{OPTION_B_CONS}}

### Option C — {{OPTION_C_NAME}}

{{OPTION_C_DESCRIPTION}}

**Pros:** {{OPTION_C_PROS}}  
**Cons:** {{OPTION_C_CONS}}

---

## Recommendation

<!--
Which option and why, in terms of the project's constraints (stack, scale, goals).
Must reference at least one acceptance criterion from the requirements and show this option satisfies it.
If introducing a new dependency, justify it here in one sentence and flag it: [requires human approval].
3-5 sentences maximum.
-->

{{RECOMMENDATION}}

---

## Implementation guidance

<!--
The specification the developer agent will follow. Be concrete: names, types, paths, contracts.
No pseudocode unless the algorithm is the decision itself.
Remove subsections that do not apply to this decision.
-->

### Data model

<!-- Table or list of fields with type, constraints, and description. Include storage name and indexes if relevant. -->

| Field | Type | Constraints | Description |
|---|---|---|---|
| {{FIELD}} | {{TYPE}} | {{CONSTRAINTS}} | {{DESCRIPTION}} |

### Interface contract

<!-- One block per endpoint or function exposed. Method/path/shapes/status codes/error cases, or function signatures. Remove if this decision exposes no interface. -->

#### `{{METHOD}} {{PATH}}`

**Request:**  
```json
{{REQUEST_SHAPE}}
```

**Response ({{SUCCESS_CODE}}):**  
```json
{{RESPONSE_SHAPE}}
```

**Error cases:**
- `{{ERROR_CODE}}` — {{MEANING}}

### File and folder structure

<!-- List only new files and folders. For modified files, note what changes. -->

```text
{{PROJECT_ROOT}}/
  {{NEW_FILE_OR_FOLDER}}    ← {{PURPOSE}}
```

### Naming conventions

<!-- Any naming rules specific to this decision. If project conventions in README.md already cover it, write exactly that. -->

- {{CONVENTION}}

### Guard rails for the developer

<!-- Explicit list of things the developer must NOT do. These prevent overengineering and scope creep during implementation. -->

- Do not {{GUARD_RAIL_1}}
- Do not {{GUARD_RAIL_2}}

---

## Acceptance criteria satisfied

<!--
Copy the AC identifiers from the requirements and confirm how this design satisfies each.
Format: AC-N → [how the design satisfies it]
-->

- AC-1 → {{HOW_SATISFIED}}
- AC-2 → {{HOW_SATISFIED}}

---

## Consequences

<!-- What becomes easier and what becomes harder. Honest assessment, including technical debt introduced, if any. -->

**Easier:** {{WHAT_BECOMES_EASIER}}  
**Harder:** {{WHAT_BECOMES_HARDER}}  
**Technical debt introduced:** {{DEBT_OR_NONE}}

---

## Board updates

<!--
Per github-projects-policy.md: architect does not change item state.
Once the human approves this ADR, affected items become eligible to move Backlog -> Ready,
and planning executes that transition. Normally leave the line below unchanged.
-->

None — items affected by this ADR become eligible for `Ready` upon human approval; planning applies the transition.

---

**Approved by:** ________________  
**Approval date:** ________________  
**Next agent:** developer (+ tester in parallel)

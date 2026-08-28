# Requirements: {{FEATURE_NAME}}

**Date:** {{YYYY-MM-DD}}  
**Project:** {{PROJECT_NAME}}  
**Requested by:** human  
**Discovery:** `docs/discovery.md`  
**Status:** 🟡 pending approval

---

## Scope summary

<!--
One short paragraph. What will exist once this is done, from the user's perspective.
Apply the minimum-scope rule: only what the main use case needs to work end-to-end belongs here.
No solutions, no architecture.
-->

{{SCOPE_SUMMARY}}

---

## In scope

<!--
Numbered list. Only what will be built in this iteration.
Be specific: not "recipe CRUD" but "POST /recipes endpoint that persists name, ingredients, and instructions".
Each item must be implementable and testable on its own.
-->

1. {{IN_SCOPE_ITEM_1}}
2. {{IN_SCOPE_ITEM_2}}

---

## Out of scope

<!--
Just as important as the above. List what will explicitly NOT be done.
Include things the human might assume are covered but are not.
-->

- {{OUT_OF_SCOPE_ITEM_1}}

---

## Functional requirements

<!--
Numbered FR-N. Observable behaviors of the system, specific enough that a developer can implement
each without asking questions. No implementation choices (databases, libraries, frameworks) — that is architecture.
-->

**FR-1**  
{{FUNCTIONAL_REQUIREMENT}}

**FR-2**  
{{FUNCTIONAL_REQUIREMENT}}

---

## Non-functional requirements

<!--
NFR-N: performance, security, usability, or reliability constraints that are real — stated by the human
or clearly implied by the project. No invented numbers.
If none apply, replace this section's content with "None identified."
-->

**NFR-1**  
{{NON_FUNCTIONAL_REQUIREMENT}}

---

## Acceptance criteria

<!--
Strict format: Given / When / Then.
Must be unambiguously verifiable by the tester agent.
Minimum 2, maximum 6. If you need more than 6, the scope is too large.
Each AC must map to at least one FR above.
-->

**AC-1**  
Given {{context}}  
When {{action}}  
Then {{expected_result}}

**AC-2**  
Given {{context}}  
When {{action}}  
Then {{expected_result}}

---

## Edge cases

<!--
Inputs, states, or sequences outside the happy path that must still behave correctly:
empty states, boundary values, invalid input, repeated actions.
Only real ones grounded in the domain. If there are none, write "None identified."
-->

- {{EDGE_CASE}}

---

## Dependencies

<!--
Only real, verifiable dependencies: existing modules being touched, data that must exist,
required external services. If there are none, write "None."
-->

- {{DEPENDENCY_1}}

---

## Open questions

<!--
Decisions the human must make before planning or architecture proceeds.
Maximum 3. Blocking questions first.
If there are none, remove this section.
-->

1. {{OPEN_QUESTION}}

---

## Board updates

<!--
Per github-projects-policy.md: scopper neither creates items nor changes their state.
Normally leave the line below unchanged.
-->

None — planning owns item creation and state.

---

**Approved by:** ________________  
**Approval date:** ________________  
**Next agent:** planner

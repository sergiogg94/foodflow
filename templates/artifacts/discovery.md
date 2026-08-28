# Discovery: {{TOPIC_NAME}}

**Date:** {{YYYY-MM-DD}}  
**Project:** {{PROJECT_NAME}}  
**Requested by:** human  
**Status:** 🟡 pending approval

---

## Problem statement

<!--
One or two sentences. Describe the underlying problem, from the user's or system's perspective.
Separate what the human said from what they actually need.
Do not describe any solution here. Only the problem.
-->

{{PROBLEM_STATEMENT}}

---

## Goals

<!--
Numbered list of outcomes, not implementations.
Format: "Allow [who] to [do what] so that [why]."
If the request contains a solution disguised as a goal, restate it as an outcome here.
-->

1. {{GOAL_1}}
2. {{GOAL_2}}

---

## Non-goals

<!--
What will explicitly NOT be pursued in this effort.
Include things the human might assume are covered but are not.
-->

- {{NON_GOAL_1}}
- {{NON_GOAL_2}}

---

## Assumptions

<!--
Every assumption the framing depends on, traceable to something the human said or something visible in the repository.
Format: [We assume X] → [if wrong, impact].
Do not invent assumptions to fill space.
-->

- We assume {{ASSUMPTION}} → if wrong, {{IMPACT}}

---

## Open questions

<!--
Decisions only the human can make before scoping can proceed.
Maximum 3. One is ideal. Blocking questions first.
If there are none, remove this section.
-->

1. {{OPEN_QUESTION}}

---

## Constraints

<!--
Only real, verifiable constraints: stack decisions already made, infrastructure, data that exists,
time or budget limits stated by the human, approved ADRs that narrow the space.
No hypotheticals. If there are none beyond the obvious, write "None identified."
-->

- {{CONSTRAINT_1}}

---

## Initial risks

<!--
Only concrete risks grounded in project context. No speculative catastrophizing.
Format: [risk] → [why it matters now].
Mitigations are not your job — do not propose them.
-->

- {{RISK}} → {{WHY_IT_MATTERS}}

---

## Existing context

<!--
What already exists that is relevant to this problem: modules, files, documentation,
prior decisions. Reference paths. This prevents downstream agents from rediscovering the project.
Remove this section if nothing applies.
-->

- {{CONTEXT_ITEM_WITH_PATH}}

---

## Linked references

<!--
Links to the sources that motivated this work: issues, documents, files, prior artifacts.
Remove this section if there are none.
-->

- {{REFERENCE}}

---

## Board updates

<!--
Per github-projects-policy.md: discovery never creates items — planning owns item creation.
Normally leave the line below unchanged.
-->

None — planning owns item creation.

---

**Approved by:** ________________  
**Approval date:** ________________  
**Next agent:** scopper

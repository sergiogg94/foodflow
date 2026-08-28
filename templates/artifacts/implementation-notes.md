# Implementation notes: {{FEATURE_NAME}}

**Date:** {{YYYY-MM-DD}}  
**Project:** {{PROJECT_NAME}}  
**Requested by:** human  
**Task(s):** {{T-N_LIST}}  
**Branch:** {{BRANCH_NAME}}  
**ADR(s):** `docs/adr/{{ADR_FILENAMES}}`  
**Status:** 🟡 pending review

---

## Summary

<!--
Two to four sentences. What was built, from the reviewer's perspective.
Reference the ADR(s) followed. No narrative, no process story.
-->

{{SUMMARY}}

---

## Implementation per task

<!-- One block per task ID. What was implemented and where (real paths). Map each FR/AC touched to the code that satisfies it. -->

### T-1 — {{TASK_TITLE}}

{{WHAT_WAS_IMPLEMENTED_AND_WHERE}}

---

## Deviations from the ADR

<!--
Must read "None." Any real deviation means implementation stopped and escalated instead.
Do not normalize deviations here.
-->

None.

---

## Validation performed

<!--
Factual list of commands run and their results: tests, linters, type checkers, manual runs.
Include what was NOT validated — gaps must be visible to the tester and reviewer.
Format: command → result.
-->

- {{COMMAND}} → {{RESULT}}

---

## Follow-up issues discovered

<!--
Real problems found while implementing that are out of scope: pre-existing bugs,
missing coverage elsewhere, tech debt noticed. One line each.
These become candidate issues — planning decides. If none, write "None."
-->

- {{FOLLOW_UP}}

---

## Board updates

<!--
Suggested operations with evidence, per github-projects-policy.md.
developer may suggest: Ready -> In Progress (when starting), In Progress -> Review (PR open AND tests run).
-->

```text
Move {{TASK_ISSUE}} In Progress -> Review — evidence: PR {{PR_URL_OR_BRANCH}}
```

---

**Approved by:** ________________  
**Approval date:** ________________  
**Next agent:** tester (+ reviewer after)

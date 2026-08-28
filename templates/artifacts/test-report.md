# Test report: {{FEATURE_NAME}}

**Date:** {{YYYY-MM-DD}}  
**Project:** {{PROJECT_NAME}}  
**Requested by:** human  
**Task(s):** {{T-N_LIST}}  
**Requirements:** `docs/requirements.md`  
**Implementation notes:** `docs/notes/{{NOTES_FILENAME}}`  
**Branch:** {{BRANCH_NAME}}  
**Status:** 🟡 pending review

---

## Validation summary

<!--
Two or three sentences. What was validated, how, and the overall outcome.
Facts only: "12 tests written, 11 pass, 1 AC requires manual check."
-->

{{VALIDATION_SUMMARY}}

---

## Scope tested

<!--
What was actually exercised: behaviors, files, endpoints, paths.
List what was NOT exercised too — visible gaps prevent false confidence.
-->

**Tested:** {{SCOPE_TESTED}}  
**Not tested:** {{SCOPE_NOT_TESTED}}

---

## Acceptance criteria coverage

<!--
One row per AC from the requirements. Exactly one status each:
✅ Pass - a test proves it (reference the test)
❌ Fail - a test disproves it (reference test + defect below)
⚠️ Needs manual check - not verifiable from code alone (state what the human must do)
-->

| AC | Status | Evidence |
|---|---|---|
| AC-1 | {{✅ / ❌ / ⚠️}} | {{TEST_NAME_OR_PATH}} |
| AC-2 | {{✅ / ❌ / ⚠️}} | {{TEST_NAME_OR_PATH}} |

---

## Edge case coverage

<!--
One row per edge case from the requirements and per error case from the ADR contract.
If an edge case has no test, say so explicitly here - do not leave it silent.
-->

| Edge case / error case | Test | Result |
|---|---|---|
| {{CASE}} | {{TEST_PATH}} | {{PASS / FAIL / not covered}} |

---

## Result summary

<!-- Factual list of every command executed and its outcome. Counts: passed / failed / skipped. -->

- `{{COMMAND}}` → {{RESULT}}

**Totals:** {{PASSED}} passed · {{FAILED}} failed · {{SKIPPED}} skipped

---

## Defects observed

<!-- App-code problems found while testing. One item per defect: file:line, what happens, what should happen. Never fixed by you - reported. If none, write "None." -->

- {{FILE_AND_LINE}} — {{OBSERVED}}; expected {{EXPECTED}}

---

## Test gaps

<!--
What remains unvalidated and why: manual-only checks, environment limits, out-of-scope areas.
This is the honesty section - state remaining risk so the human can decide.
If full coverage was achieved, write "None identified."
-->

- {{GAP}} — because {{REASON}}

---

## Board updates

<!--
Per github-projects-policy.md: tester does not change item state.
Normally leave the line below unchanged.
-->

None — the reviewer consumes this report.

---

**Approved by:** ________________  
**Approval date:** ________________  
**Next agent:** reviewer

# Code review: {{FEATURE_NAME}}

**Date:** {{YYYY-MM-DD}}  
**Project:** {{PROJECT_NAME}}  
**Requested by:** human  
**Task(s):** {{T-N_LIST}}  
**Requirements:** `docs/requirements.md`  
**Implementation notes:** `docs/notes/{{NOTES_FILENAME}}`  
**Test report:** `docs/tests/{{TEST_REPORT_FILENAME}}`  
**Branch:** {{BRANCH_NAME}}  
**Status:** 🟡 pending human decision

---

## Review summary

<!-- Two or three sentences. What was reviewed and the overall outcome. Facts only: "Implementation follows the ADR except for one blocking deviation in the API error contract." -->

{{REVIEW_SUMMARY}}

---

## Scope reviewed

<!-- Files and behaviors reviewed completely (not just diffs). Note anything relevant that could not be reviewed and why. -->

{{SCOPE_REVIEWED}}

---

## Acceptance criteria cross-check

<!-- Independent verification of the tester's claims. Agree or document the discrepancy. Statuses: ✅ verified · ❌ contradicts test report · ⚠️ needs manual check -->

| AC | Tester status | Reviewer verification |
|---|---|---|
| AC-1 | {{STATUS}} | {{AGREES / DISCREPANCY_DETAIL}} |
| AC-2 | {{STATUS}} | {{AGREES / DISCREPANCY_DETAIL}} |

---

## Findings

<!-- One finding per item. Never bundle two issues. Each 🔴 and 🟡 finding must include file:line, description, and a concrete fix suggestion. Do not rewrite code here. -->

### 🔴 Blocking

<!-- Must be fixed before merge. The PR cannot be approved in its current state. If none, write "None." -->

**B-1** — `{{FILE_AND_LINE}}`  
{{DESCRIPTION_OF_DEVIATION_OR_DEFECT}}  
**Fix:** {{CONCRETE_SUGGESTION}}

### 🟡 Non-blocking

<!-- Worth fixing but does not prevent merge. Human decides. If none, write "None." -->

**NB-1** — `{{FILE_AND_LINE}}`  
{{DESCRIPTION}}  
**Fix:** {{CONCRETE_SUGGESTION}}

### 🟢 Positive

<!-- Only quality genuinely above the expected standard. No praise for effort. If nothing merits it, write "None." -->

**P-1** — `{{FILE_AND_LINE}}`  
{{WHAT_WAS_DONE_PARTICULARLY_WELL}}

---

## Final recommendation

<!--
Exactly one verdict, consistent with the findings above:
- "Approved" - zero blocking findings; human may merge
- "Changes requested" - one or more blocking findings; developer addresses, then re-review
- "Escalate to human" - fixing requires changing the ADR or an architectural decision
-->

{{VERDICT}} — {{ONE_SENTENCE_JUSTIFICATION}}

---

## Board updates

<!-- Recommendation implied by the verdict. Per github-projects-policy.md the reviewer recommends; never executes. -->

```text
{{e.g. Move T-1 Review -> In Progress after developer addresses B-1 | Hold in Review pending human merge decision}}
```

---

**Decision by:** ________________ *(human)*  
**Date:** ________________  
**Next step:** ✅ → documenter + merge · 🔄 → developer re-work · ⛔ → architect/human decision

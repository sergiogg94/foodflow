# Delivery checklist: {{FEATURE_NAME}}

**Date:** {{YYYY-MM-DD}}  
**Project:** {{PROJECT_NAME}}  
**Requested by:** human  
**Tasks:** {{T-N_LIST}}  
**Requirements:** `docs/requirements.md`  
**Implementation notes:** `docs/notes/{{NOTES_FILENAME}}`  
**Test report:** `docs/tests/{{TEST_REPORT_FILENAME}}`  
**Review report:** `docs/reviews/{{REVIEW_FILENAME}}`  
**Status:** 🟡 pending human acceptance

---

## Scope delivered

<!--
What of the requested scope is actually delivered, stated plainly.
Map to the requirements' in-scope items: delivered / partially delivered / not delivered.
No optimism: partial is partial.
-->

- {{IN_SCOPE_ITEM_1}} — {{delivered / partial / not delivered}}
- {{IN_SCOPE_ITEM_2}} — {{STATUS}}

---

## Requirements reference

<!-- Final state of every acceptance criterion, consolidating test report and review cross-check. Statuses: ✅ Pass · ❌ Fail · ⚠️ Needs manual check -->

| AC | Final status | Evidence |
|---|---|---|
| AC-1 | {{STATUS}} | {{test/report reference}} |
| AC-2 | {{STATUS}} | {{test/report reference}} |

---

## Implementation reference

<!-- Where the delivered work lives: branch, PR, commit range, notes document. Real links and identifiers only. -->

- **Branch:** {{BRANCH_NAME}}
- **Pull request:** {{PR_URL_OR_NONE_YET}}
- **Commits:** {{RANGE_OR_COUNT}}

---

## Review status

<!-- Verdict from the review report and its consequences. If Changes were Requested and addressed, say so and reference the re-review. -->

- **Verdict:** {{✅ Approved / 🔄 Changes requested / ⛔ Escalated}}
- **Blocking findings:** {{COUNT_AND_STATE}}
- **Report:** `docs/reviews/{{REVIEW_FILENAME}}`

---

## Test status

<!-- Consolidated validation outcome: totals, coverage state, and the honest remainder. -->

- **Results:** {{PASSED}} passed · {{FAILED}} failed · {{SKIPPED}} skipped
- **Coverage gaps:** {{GAPS_OR_NONE}} — detail in `docs/tests/{{TEST_REPORT_FILENAME}}`

---

## Documentation status

<!-- Which documents were updated as part of this delivery, and which still need updating. -->

- {{DOC_UPDATED}} — updated
- {{DOC_PENDING}} — pending

---

## Open risks

<!--
Known remaining risks after delivery: unverified areas, deferred work, accepted debt.
Consolidated from test gaps, review findings, and implementation notes. If none, write "None identified."
-->

- {{RISK_WITH_SOURCE_ARTIFACT}}

---

## Final checklist

<!--
Every condition the human should confirm before accepting. Include human-only actions explicitly.
Mark each box's current state honestly: checked only if an artifact proves it.
-->

- [ ] Review verdict: ✅ Approved
- [ ] Zero 🔴 blocking findings unresolved
- [ ] All ACs ✅ or explicitly accepted as ⚠️ manual checks
- [ ] Test suite passes; failures accounted for
- [ ] Documentation updated or consciously deferred
- [ ] Human merges the pull request
- [ ] Human accepts the delivery

---

## Board updates

<!-- Per github-projects-policy.md: only the human marks items Done. This checklist proposes; the human disposes. -->

```text
Upon human acceptance: move {{TASK_ISSUES}} to Done — evidence: this checklist + merged PR
```

---

**Accepted by:** ________________ *(human)*  
**Acceptance date:** ________________

# Artifact Contracts

## Purpose

This document defines the MVP output contracts for `conductor`.

Its purpose is to standardize what each agent should produce so that:

- work can move cleanly from one stage to the next
- outputs are reviewable by a human
- artifacts can be reused as durable context
- task tracking can stay aligned with execution
- projects can apply the framework consistently

In `conductor`, agents should collaborate through artifacts, not through long, unstructured conversations.

## Design Principles

All artifact contracts in the MVP follow these principles:

1. Every important stage should leave a durable artifact.
2. Artifacts should be understandable by humans without needing the full chat history.
3. Artifacts should be structured enough to support handoffs.
4. Artifacts should be lightweight in the MVP.
5. Artifacts should prefer clarity over completeness.
6. If an agent cannot confidently produce a required artifact, it should explicitly list open questions and assumptions.

## Contract Model

Each artifact contract defines:

- owner agent
- purpose
- default path
- required sections
- optional sections
- completion criteria
- downstream consumers

## Global Rules

### 1. Do not invent missing facts

If required information is missing, the artifact must explicitly list:
- assumptions
- unanswered questions
- missing inputs

### 2. Prefer explicit structure

Artifacts should use stable headings and predictable sections whenever possible.

### 3. Preserve scope boundaries

Artifacts should not silently expand scope. Optional ideas or future improvements must be clearly separated from in-scope work.

### 4. Be implementation-aware, but role-correct

Each agent should write from its role:
- discovery frames the problem
- scopper defines scope
- planner defines execution units
- architect defines technical direction
- developer implements
- reviewer evaluates
- tester validates
- docs documents

### 5. Artifacts should be easy to diff

Whenever possible, artifacts should be updated incrementally and remain readable in version control.

## Artifact Inventory

The MVP defines the following core artifacts:

1. Discovery Artifact
2. Requirements Artifact
3. Implementation Plan Artifact
4. Architecture Artifact
5. Review Report Artifact
6. Test Report Artifact
7. Delivery Checklist Artifact

Additional project-specific artifacts may be added later, but these are the core framework contracts for the MVP.

---

## 1. Discovery Artifact

### Owner Agent

`discovery`

### Purpose

Capture the initial understanding of the problem before scoping or implementation begins.

### Default Path

`docs/discovery.md`

### Required Sections

- Title
- Problem Statement
- Goals
- Non-Goals
- Assumptions
- Open Questions
- Constraints
- Initial Risks

### Optional Sections

- Stakeholders
- User Personas
- Existing Context
- Linked References

### Completion Criteria

A discovery artifact is complete when:
- the core problem is clearly stated
- goals and non-goals are distinguished
- major assumptions are explicit
- key open questions are captured
- downstream scoping can begin without relying on hidden context

### Downstream Consumers

- `scopper`
- `planner`
- `architect`
- human reviewer

---

## 2. Requirements Artifact

### Owner Agent

`scopper`

### Purpose

Convert the discovery output into a scoped, testable description of what should be built.

### Default Path

`docs/requirements.md`

### Required Sections

- Title
- Scope Summary
- In-Scope
- Out-of-Scope
- Functional Requirements
- Non-Functional Requirements
- Acceptance Criteria
- Edge Cases
- Dependencies
- Open Questions

### Optional Sections

- User Flows
- Constraints by Environment
- Follow-Up Opportunities
- Release Notes Considerations

### Completion Criteria

A requirements artifact is complete when:
- scope boundaries are clear
- the work can be tested against acceptance criteria
- edge cases are documented at an appropriate level
- unclear areas are explicitly marked
- planning can break work into tasks without guessing the goal

### Downstream Consumers

- `planner`
- `architect`
- `developer`
- `tester`
- human reviewer

---

## 3. Implementation Plan Artifact

### Owner Agent

`planner`

### Purpose

Translate the requirements into executable work units and project tracking structure.

### Default Path

`docs/implementation-plan.md`

### Required Sections

- Title
- Planning Summary
- Task Breakdown
- Suggested Issue Structure
- Priority Order
- Dependencies and Blockers
- GitHub Projects Mapping
- Suggested Execution Sequence

### Optional Sections

- Parallelizable Work
- Deferred Work
- Labels or Tags
- Suggested Ownership

### Completion Criteria

An implementation plan artifact is complete when:
- the scoped work is broken into manageable tasks
- priorities are clear
- dependencies are visible
- board-ready task structure exists
- architecture and development can begin with a defined work map

### Downstream Consumers

- `architect`
- `developer`
- `devops`
- human reviewer
- GitHub Issues / GitHub Projects workflow

---

## 4. Architecture Artifact

### Owner Agent

`architect`

### Purpose

Define the technical approach for implementing the scoped work.

### Default Path

`docs/architecture.md`

### Required Sections

- Title
- Technical Summary
- Existing Context
- Proposed Changes
- Components or Modules Affected
- Data Flow or Interaction Notes
- Interfaces or API Changes
- Risks and Tradeoffs
- Open Technical Questions

### Optional Sections

- ADR References
- Migration Notes
- Operational Considerations
- Performance Considerations
- Security Considerations

### Completion Criteria

An architecture artifact is complete when:
- the implementation direction is understandable
- affected parts of the system are identified
- major technical tradeoffs are visible
- unresolved technical questions are explicit
- the developer can implement without inventing the design

### Downstream Consumers

- `developer`
- `reviewer`
- `tester`
- `devops`
- human reviewer

---

## 5. Review Report Artifact

### Owner Agent

`reviewer`

### Purpose

Evaluate the implementation against quality, maintainability, and correctness expectations.

### Default Path

`docs/reviews/<task-or-pr-name>.md`

### Required Sections

- Title
- Review Summary
- Scope Reviewed
- Findings
- Severity per Finding
- Suggested Fixes
- Final Recommendation

### Optional Sections

- Maintainability Notes
- Consistency Notes
- Follow-Up Suggestions
- Positive Observations

### Completion Criteria

A review report is complete when:
- the reviewed scope is clear
- findings are specific and actionable
- severity is explicit
- the recommendation is understandable by a human and the developer
- unclear or risky areas are highlighted

### Downstream Consumers

- `developer`
- `tester`
- human reviewer
- pull request workflow

---

## 6. Test Report Artifact

### Owner Agent

`tester`

### Purpose

Capture how the implementation was validated against requirements and acceptance criteria.

### Default Path

`docs/tests/<task-or-pr-name>.md`

### Required Sections

- Title
- Validation Summary
- Scope Tested
- Acceptance Criteria Coverage
- Test Gaps
- Edge Case Coverage
- Result Summary

### Optional Sections

- Suggested Additional Tests
- Regression Risk Notes
- Environment Notes
- Manual Validation Notes

### Completion Criteria

A test report is complete when:
- the tested scope is clear
- acceptance criteria coverage is addressed
- missing validation is explicit
- edge cases are considered
- the human can understand confidence and remaining risk

### Downstream Consumers

- `developer`
- `reviewer`
- `docs`
- human reviewer
- release or completion decision

---

## 7. Delivery Checklist Artifact

### Owner Agent

`docs`  
with possible contributions from `reviewer`, `tester`, and `devops`

### Purpose

Provide a concise delivery-facing summary of whether the work is ready to be considered complete.

### Default Path

`docs/delivery-checklist.md`

### Required Sections

- Title
- Scope Delivered
- Requirements Reference
- Implementation Reference
- Review Status
- Test Status
- Documentation Status
- Open Risks
- Final Checklist

### Optional Sections

- Linked Pull Requests
- Deployment Notes
- Rollback Notes
- Follow-Up Work

### Completion Criteria

A delivery checklist artifact is complete when:
- the delivered scope is clearly stated
- the state of review, testing, and documentation is visible
- any remaining risks are explicit
- a human can use it as a final readiness checkpoint

### Downstream Consumers

- human reviewer
- release workflow
- project tracking workflow

---

## Artifact-to-Agent Mapping

| Artifact | Owner | Primary Consumers |
|---|---|---|
| `docs/discovery.md` | `discovery` | `scopper`, `planner`, `architect` |
| `docs/requirements.md` | `scopper` | `planner`, `architect`, `developer`, `tester` |
| `docs/implementation-plan.md` | `planner` | `architect`, `developer`, `devops` |
| `docs/architecture.md` | `architect` | `developer`, `reviewer`, `tester`, `devops` |
| `docs/reviews/<name>.md` | `reviewer` | `developer`, `tester`, human |
| `docs/tests/<name>.md` | `tester` | `developer`, `reviewer`, `docs`, human |
| `docs/delivery-checklist.md` | `docs` | human, release/closure flow |

---

## Minimum Handoff Expectations

For the MVP, the minimum expected handoff chain is:

1. `discovery` produces `docs/discovery.md`
2. `scopper` produces `docs/requirements.md`
3. `planner` produces `docs/implementation-plan.md`
4. `architect` produces `docs/architecture.md`
5. `developer` implements code changes using prior artifacts
6. `reviewer` produces a review report when needed
7. `tester` produces a test report when needed
8. `docs` updates documentation and delivery checklist

Not every task must generate every artifact in full detail, but the framework should prefer durable written outputs for important work.

## Lightweight Artifact Policy for the MVP

The MVP should avoid heavy process overhead.

That means:
- short artifacts are acceptable
- concise sections are acceptable
- not every artifact must be exhaustive
- low-risk work may produce smaller reports
- artifacts should scale with task complexity

However, even lightweight artifacts must remain structured and useful.

## Project Tracking Alignment

Artifacts should align with GitHub work tracking wherever possible.

Recommended alignment:
- requirements and planning artifacts support issue creation
- planning artifacts support GitHub Project item creation and prioritization
- review and test artifacts support status transitions into review or done
- delivery checklist supports final completion review

Artifacts should reinforce project state, not drift away from it.

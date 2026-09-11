---
description: Board synchronization - compares GitHub Projects state against repository reality and reconciles it. With github_mcp enabled, permissioned operations (create, move, update within the planner row) are applied via MCP; human-owned gates (Done, Blocked, priority) are reported for the human to act on.
agent: planner
---

Run one Project synchronization pass.

Scope filter from the human (optional): $ARGUMENTS

Follow the interaction rules of github-projects-policy.md. Read the current artifacts and repository state, compare them against what the board should reflect, and reconcile the difference. When `github_mcp: true` and your `can_update_projects` covers the operation (create items, add to project, set Status/Type/Priority/Effort at creation), execute it via MCP tools (`mcp__github`) and record what you changed. Everything outside your permissions — `Done`, `Blocked` resolution, priority changes after creation — goes into the `## Board updates` report for the human to apply. Never mutate what the policy forbids even if MCP would allow it.

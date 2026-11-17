# Devpost submission draft — CereX Local Context Graph

> **Working text for the Relate by Neo4j Hackathon.** This is **not** an official Devpost submission receipt. Validate the information in the Devpost form before publishing.

## Project name
CereX Local Context Graph — Permission-Aware Computer Agents

## Elevator pitch
A persistent Relate graph helps explain exactly which user-authorized computer workflow steps can proceed, which must stop, and how blocked dependencies affect the entire plan.

## What it does
AI assistants can request complex computer workflows, but their action plans are often missing an inspectable connection between task dependencies, owner-granted capabilities, human approval, and expected evidence. CereX Local Context Graph provides an explicit **preflight decision layer**: every workflow step has named prerequisites and permissions. Relate stores those relationships in an actual persistent embedded graph, which the preflight engine traverses with Cypher.

Our live synthetic sample contains 8 workflow tasks, 6 dependency edges, 4 plan-level permitted tasks and 4 denied tasks. Examples include a blocked network send, an unapproved shell action, and a task whose predecessor is missing. Dependencies can propagate denials downstream. The accompanying browser page displays graph-backed reasoning and supports inspection by judges without an account.

This is a **prototype using synthetic data**. Its 'PERMITTED' result means only that the policy preflight passed. It does not execute PC commands. Existing CereX's owner-controlled real-device executor is **pre-existing**, not claimed as newly developed for this contest.

## Why Relate matters
The core challenge is not issuing an agent command; it is preserving connected context between instructions, capabilities, human decisions, devices, dependencies and evidence. An embedded persistent graph makes those links queryable and explainable. The prototype uses genuine **Relate DB 1.0.1**, not a JavaScript graph imitation or hardcoded result list.

## How we built it
- Built a new standalone competition adapter during the hackathon period, starting November 14, 2026
- Used Python 3.10, pinned `relate-db==1.0.1`, a persistent `judge-graph.rl` store, and six fixed read-only Cypher queries
- Modeled Task, Device, Capability, Approval and Evidence nodes with dependencies and authorization relationships
- Built a small browser-based judge viewer, constrained local-only read API and synthetic fixtures
- Added unit tests covering persistence, Cypher, permissions, dependencies and boundaries; **7/7 currently pass**
- AI-assisted development was used; project authors remain responsible for all implementation, testing and original work
- The original CereX computer agent existed before the hackathon; only this new graph preflight adapter is the contest entry

## Challenges
Balancing useful graph reasoning with conservative permissions; keeping the Relate store reproducible and the public judge demonstration isolated from any real credentials; making denial reasons deterministic and testable; and distinguishing simulated permission results from verified real-device execution.

## What we learned
Graph-based task context can explain *why* a dependent step fails, not just which single action failed. A persistent graph also gives judges and developers a repeatable state to inspect independently.

## What's next
Connect this preflight to actual owner-approved CereX requests in a separate opt-in integration, add safe policy revocation UAT and signed execution receipts, and test with user-owned devices. These are planned improvements, **not currently demonstrated** by the Relate adapter.

## Tech stack
Relate DB 1.0.1, Cypher, Python 3.10, JavaScript, HTML/CSS, unittest, GitHub Actions. Synthetic data only. AI-assisted coding disclosed.

## Public judge links
- **Interactive live demo:** https://cerex.site/judge/relate-live/
- **Public source & setup:** https://github.com/sahamgorengancuan-prog/cerex-relate-context-graph
- **Read-only graph API:** https://cerex.site/judge/relate-api/graph
- **Live health check:** https://cerex.site/judge/relate-api/health

## Official submission requirements still to verify
- [ ] GitHub repo has required topic `relate` (GitHub API currently reports zero topics)
- [ ] Devpost project actually created under correct registered competition account
- [ ] Devpost fields reviewed and official final submission receipt verified
- [ ] Optional 1–2-minute demo video if adding one (working demo URL already available)

## Demo video outline (if needed, target 110 seconds)
- 00:00–00:12: Permissioned computer workflow problem and the new graph preflight
- 00:12–00:32: Real Relate 1.0.1 database and task graph view
- 00:32–00:58: Show a PERMITTED synthetic CSV read and why it passes
- 00:58–01:25: Show blocked network send and permission/approval reason
- 01:25–01:43: Show dependency failure propagation and missing predecessor
- 01:43–01:50: End with 7/7 test results and link; clearly note synthetic preflight only

No music or third-party footage is required. Any recorded video must show the actual working application, not invented execution.

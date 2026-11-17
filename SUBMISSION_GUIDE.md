# Relate Devpost submission — judge-oriented publication checklist

## Entrant scope
This repository includes **only** the new Relate local-context-graph preflight adapter and synthetic examples, written during the Nov 11–Dec 11, 2026 contest period. The original CereX local PC agent is pre-existing and is **not** included in this release or advertised as newly built.

## Required GitHub publication
1. Create **new public** repository `cerex-relate-context-graph` under your GitHub account.
2. Push exactly these prepared source files, including the persistent `judge-graph.rl` and automated tests.
3. Open GitHub repo About -> Topics; add mandatory `relate`, optionally `relate-neo4j-hackathon`.
4. Verify public anonymous access, runnable clone, and Actions tests pass.
5. Submit official Devpost form only after a real draft is created and all fields are checked.

## Live demo
https://cerex.site/judge/relate-live/

## Local repro
```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python engine.py
```

## Judge disclosure (important)
The actual Relate graph, Relate 1.0.1 embedded persistence and fixed Cypher queries are functional. All policy decisions use synthetic data, and PERMITTED denotes a plan-level result, **not** real CereX PC remote execution. No live machine command or permission revocation is demonstrated by this adapter yet. Third-party agent permission enforcement still belongs to the pre-existing CereX system.

## Devpost entry field draft
Title: CereX Local Context Graph — Permission-Aware Computer Agents

Tagline: A Relate-backed graph preflight explains the allowed, denied, and dependency-blocked steps of user-authorized computer workflows.

What it does: An external AI can request an owner-scoped local-computer workflow. Before execution, a separate Relate module stores tasks, tools, human approvals, dependency edges and evidence references as one inspectable persistent graph. Deterministic Cypher-driven checks classify the synthetic workflow steps with detailed reasons and demonstrate propagation of denied prerequisites.

How Relate is used: Embedded `relate-db==1.0.1`, `judge-graph.rl` persistent on-disk store, six read-only Cypher traversals covering tasks, capabilities, approvals, dependencies and evidence. No simulated graph dependency is substituted.

Built with: Python 3.10, Relate DB 1.0.1, JavaScript UI, synthetic fixtures, deterministic tests; AI-assisted coding disclosed. Pre-existing CereX platform described for architecture context but excluded from new-code claim.

Caveat: Prototype is a graph authorization *preflight*, not a demonstrated live connection to a real PC. The linked interactive demo runs real Relate server queries against a synthetic store.

Links: https://cerex.site/judge/relate-live/ ; public GitHub repo URL (insert only after created), optional video URL (insert only after published).

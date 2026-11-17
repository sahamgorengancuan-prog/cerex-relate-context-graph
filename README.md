# CereX Local Context Graph — Relate Hackathon 2026

**Status:** new standalone Relate 1.0.1 integration started 2026-11-14. This is a live graph preflight prototype using exclusively synthetic data, not a CereX remote-device execution session.

Judge demo: https://cerex.site/judge/relate-live/

Universal demo hub: https://cerex.site/judge/?track=relate#missions

## Problem and breakthrough

AI assistants coordinating local-computer tasks lack compact, verifiable context about which task depends on which prerequisite, which device capabilities an owner has permitted, and whether a human approved a risky step. A textual log cannot always explain why an action should be blocked, or why its descendants should be blocked as well. This extension makes execution preflight graph-queryable and auditable rather than trusting an LLM's confidence.

## New work versus existing CereX

The newly constructed contest component is the Relate context graph, deterministic preflight, and interactive judge UI. The CereX platform is pre-existing and is explicitly excluded from claimed newly built work. CereX has NO embedded LLM: the user selects their AI client and allows local PC actions. This prototype does not send commands to a real PC; the separate CereX endpoint remains unchanged.

## How we use Relate — real embedded engine

- Package: relate-db==1.0.1 (actual Relate Python extension).
- Mode: persistent single-file store judge-graph.rl, checked into this package and inspectable. Not a simulated JavaScript graph.
- Graph nodes: Task, Device, Capability, Approval, Evidence.
- Graph relationships: DEPENDS_ON, RUNS_ON, REQUIRES, AUTHORIZED_BY, PROVES.
- engine.py executes SIX fixed parameter-free read-only Cypher queries on Relate and aggregates graph-derived authorization/dependency decisions.
- Query results expose eight synthetic tasks: four predicted permitted, four denied. Six actual dependency edges, one missing predecessor. A denied action propagates its blocked status to dependent tasks.

## Run locally in two minutes

Requirements: Python 3.9 or later (tested on Linux Python 3.10).

Linux/macOS:

    python3 -m venv .venv
    .venv/bin/python -m pip install -r requirements.txt
    .venv/bin/python engine.py
    .venv/bin/python -m unittest discover -s tests -v

Windows PowerShell:

    py -m venv .venv
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    .\.venv\Scripts\python.exe engine.py
    .\.venv\Scripts\python.exe -m unittest discover -s tests -v

engine.py reads the bundled .rl store read-only, emits a JSON execution preflight and never executes an OS command. seed.py can reconstruct the fixture as a new database and refuses to overwrite an existing graph file.

Inspect with Relate CLI, if independently installed from relatedb.ai:

    relate --database ./judge-graph.rl --read-only "MATCH (t:Task) RETURN t.id,t.title"
    relate --database ./judge-graph.rl --read-only "MATCH (t:Task)-[:DEPENDS_ON]->(d:Task) RETURN t.id,d.id"

Or use the Python client:

    import relate
    with relate.connect("./judge-graph.rl", read_only=True) as db:
        for r in db.execute("MATCH (t:Task)-[:REQUIRES]->(c:Capability) RETURN t.id AS task,c.id AS cap"):
            print(r)

## Hosted judge API

- GET https://cerex.site/judge/relate-api/health
- GET https://cerex.site/judge/relate-api/graph
- GET https://cerex.site/judge/relate-api/task/T-04

The hosted API permits only three fixed read endpoints, runs behind HTTPS and binds to 127.0.0.1. No arbitrary Cypher, live credentials, data upload or device execution is exposed.

## Test scenarios

- synthetic CSV read, validation and local-report tasks: graph preflight permits
- network send action: denied because not on device owner's tool allowlist, approval missing, network prohibited
- unrestricted shell: denied because not on allowlist, no approval
- non-existent predecessor T-99: denied, auditable missing-reference node
- downstream task depending on a denied network send: denied

The word PERMITTED means eligible in this synthetic planning check only. Real CereX on-device policy remains the authoritative enforcement for actual OS actions. Not a certification, an agent behavior benchmark, or a GUI/LLM efficacy claim.

## Project packaging and integrity

The repository contains the complete synthetic store, fixture, Python source, browser frontend, deterministic tests, MIT license and pinned requirements. No employee, customer, company, token, password or personal device data is included. A judge can reproduce the claimed findings entirely offline after installing Relate.

## AI assistance and third-party license

Development was AI-assisted. Implementation tested with Relate Cypher and a fresh browser. The new adapter source is MIT licensed; Relate is an independent third-party project licensed under its own terms.

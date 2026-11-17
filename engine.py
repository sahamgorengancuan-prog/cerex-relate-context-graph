#!/usr/bin/env python3
"""Verifiable, read-only execution-preflight plan derived from a real Relate 1.x graph.

This NEVER executes tasks on a PC. It queries Relate for topology, approval decisions
and device capability constraints, and returns a deterministic, inspectable plan.
All data in the included graph is synthetic. No employer, user or device data.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from typing import Any
import relate

STORE = Path(__file__).resolve().parent / "judge-graph.rl"

QUERIES = {
 "tasks": "MATCH (t:Task) RETURN t.id AS id, t.title AS title, t.requires AS requested_tool, t.expected_result AS expected_result ORDER BY id",
 "device": "MATCH (d:Device) RETURN d.id AS id, d.name AS name, d.allowed_tools AS allowed_tools, d.network_allowed AS network_allowed",
 "topology": "MATCH (t:Task)-[:DEPENDS_ON]->(d:Task) RETURN t.id AS task, d.id AS depends_on ORDER BY task",
 "capabilities": "MATCH (t:Task)-[:REQUIRES]->(c:Capability) RETURN t.id AS task, c.id AS tool, c.sensitivity AS sensitivity ORDER BY task",
 "approvals": "MATCH (t:Task)-[:AUTHORIZED_BY]->(a:Approval) RETURN t.id AS task, a.decision AS decision ORDER BY task",
 "missing": "MATCH (t:Task)-[:PROVES]->(e:Evidence) RETURN t.id AS task, e.kind AS kind, e.digest AS reference ORDER BY task",
}

def rows(query_key:str)->list[dict[str,Any]]:
    if query_key not in QUERIES: raise ValueError("Only predefined safe Relate queries are allowed.")
    if not STORE.exists(): raise RuntimeError("Missing Relate store.")
    with relate.connect(str(STORE),read_only=True) as conn:
        return [dict(r) for r in conn.execute(QUERIES[query_key])]

def snapshot()->dict[str,Any]:
    # The graph relationships below are read from Relate, not a hardcoded JS fixture.
    queried={key: rows(key) for key in QUERIES}
    devices=queried["device"]
    if len(devices)!=1: raise RuntimeError("Expected exactly one synthetic demo device.")
    node_ids={x["id"] for x in queried["tasks"]}
    device=devices[0]
    tool_allowlist={x.strip() for x in device["allowed_tools"].split(",")}
    cap_by_task={x["task"]:x for x in queried["capabilities"]}
    approval_by_task={x["task"]:x["decision"] for x in queried["approvals"]}
    dep_map={i:[] for i in node_ids}
    for edge in queried["topology"]:
        if edge["task"] not in dep_map or edge["depends_on"] not in node_ids:
            raise RuntimeError("Unknown dependency in graph")
        dep_map[edge["task"]].append(edge["depends_on"])
    missing_map={i:[] for i in node_ids}
    for e in queried["missing"]:
        missing_map[e["task"]].append(e["reference"])
    tasks_by_id={t["id"]:t for t in queried["tasks"]}
    decisions={}
    visited=set()
    def decide(task_id:str,stack:tuple[str,...]=())->dict:
        if task_id in decisions:return decisions[task_id]
        if task_id in stack:return {"id":task_id,"status":"DENIED","reasons":["Dependency cycle detected"]}
        t=tasks_by_id[task_id]
        why=[]
        cap=cap_by_task.get(task_id)
        if cap is None:why.append("No capability edge in persistent Relate graph")
        elif cap["tool"] not in tool_allowlist:
            why.append("Capability "+cap["tool"]+" is absent from device owner allowlist")
        if approval_by_task.get(task_id)!="approved":
            why.append("No positive human authorization in the Relate approval record")
        if cap and cap["tool"]=="network_send" and not bool(device["network_allowed"]):
            why.append("Device policy forbids network transfers")
        for missing_ref in missing_map[task_id]:
            why.append("Missing predecessor referenced: "+missing_ref)
        for predecessor in sorted(dep_map[task_id]):
            upstream=decide(predecessor,stack+(task_id,))
            if upstream["status"]!="PERMITTED":
                why.append("Dependency "+predecessor+" is denied")
        result={"id":task_id,"title":t["title"],"status":"DENIED" if why else "PERMITTED",
                "reasons":why if why else ["Capability allowed, human approval present, predecessors approved"],
                "requested_tool":cap["tool"] if cap else "MISSING",
                "deps":sorted(dep_map[task_id]),"expected_result":t["expected_result"]}
        decisions[task_id]=result
        return result
    evaluated=[decide(x) for x in sorted(node_ids)]
    for t in evaluated:
        t["predicted_only"]=True
    digest=hashlib.sha256(STORE.read_bytes()).hexdigest()
    return {
      "status":"READ_ONLY_PREFLIGHT_NOT_EXECUTION",
      "database":"Relate 1.0.1 embedded property graph",
      "relate_version":relate.__version__,
      "data_provenance":"Synthetic contest fixture only",
      "verified_query_count":len(QUERIES),
      "graph_sha256":digest,
      "device":{"id":device["id"],"name":device["name"],"policy":{"allow_tools":sorted(tool_allowlist),"network_allowed":bool(device["network_allowed"])}},
      "tasks":evaluated,
      "edges":queried["topology"],
      "counts":{"tasks":len(evaluated),"permitted":sum(t["status"]=="PERMITTED" for t in evaluated),"denied":sum(t["status"]=="DENIED" for t in evaluated),"dependency_edges":len(queried["topology"]),"missing_references":len(queried["missing"])},
      "limitations":["This service NEVER connects to or controls an actual laptop","It queries a real persistent Relate graph but plans only","Every device/task/receipt in the graph is synthetic","Full CereX remote execution needs separately verified owner opt-in"]
    }

def task_detail(task_id:str)->dict[str,Any]|None:
    snap=snapshot()
    return next((t for t in snap["tasks"] if t["id"]==task_id),None)

if __name__=="__main__":
    print(json.dumps(snapshot(),indent=2))

#!/usr/bin/env python3
"""New, synthetic, contest-only CereX Relate context graph; no production data."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import relate

BASE = Path(__file__).resolve().parent
STORE = BASE / "judge-graph.rl"
FIXTURE = BASE / "fixture.json"

def fixture():
    return {
      "dataset": "synthetic-v1",
      "device": {"id":"judge-demo-laptop","name":"Judge Demo Laptop (synthetic)", "owner":"Demo Owner", "allowed_tools":"python,csv_read", "network_allowed":False},
      "capabilities": [
        {"id":"csv_read","label":"Read only a selected sample CSV","sensitivity":"low"},
        {"id":"python","label":"Run constrained local Python","sensitivity":"medium"},
        {"id":"network_send","label":"Transfer data over a network","sensitivity":"high"},
        {"id":"shell","label":"Execute unrestricted shell","sensitivity":"critical"}
      ],
      "tasks":[
        {"id":"T-01","title":"Read synthetic sales CSV","requires":"csv_read","depends":[],"approval":True,"expected_result":"sample_hash"},
        {"id":"T-02","title":"Validate and summarize rows","requires":"python","depends":["T-01"],"approval":True,"expected_result":"issues.json"},
        {"id":"T-03","title":"Generate local report","requires":"python","depends":["T-02"],"approval":True,"expected_result":"report.csv"},
        {"id":"T-04","title":"Email private dataset to public inbox","requires":"network_send","depends":["T-03"],"approval":False,"expected_result":"not authorized"},
        {"id":"T-05","title":"Run unrestricted shell cleanup","requires":"shell","depends":["T-03"],"approval":False,"expected_result":"not authorized"},
        {"id":"T-06","title":"Publish summary before validation","requires":"python","depends":["T-99"],"approval":True,"expected_result":"must fail due missing dependency"},
        {"id":"T-07","title":"Reconcile independent notes","requires":"python","depends":["T-01"],"approval":True,"expected_result":"notes.json"},
        {"id":"T-08","title":"Finalize after denied network task","requires":"python","depends":["T-04"],"approval":True,"expected_result":"must fail due blocked dependency"}
      ]
    }

def add_node(db,label,props):
    labels={"Device","Task","Capability","Approval","Evidence"}
    if label not in labels: raise ValueError("invalid label")
    db.execute("CREATE (n:"+label+" {id:$id})", {"id":props["id"]})
    for key,value in props.items():
        if key=="id":continue
        if key not in {"name","owner","allowed_tools","network_allowed","label","sensitivity","title","requires","approval","expected_result","decision","digest","kind","dataset"}:
            raise ValueError("invalid property: "+key)
        db.execute("MATCH (n:"+label+" {id:$id}) SET n."+key+"=$value",{"id":props["id"],"value":value})

def attach(db,src_label,src_id,rel,dst_label,dst_id):
    for value,allowed in [(src_label,{"Device","Task","Capability","Approval","Evidence"}),(dst_label,{"Device","Task","Capability","Approval","Evidence"}),(rel,{"REQUIRES","RUNS_ON","DEPENDS_ON","AUTHORIZED_BY","PROVES"})]:
        if value not in allowed:raise ValueError("invalid topology element")
    q="MATCH (a:"+src_label+" {id:$src}), (b:"+dst_label+" {id:$dst}) CREATE (a)-[:"+rel+"]->(b)"
    db.execute(q,{"src":src_id,"dst":dst_id})

def main():
    obj=fixture()
    FIXTURE.write_text(json.dumps(obj,indent=2)+"\n")
    if STORE.exists():
        raise SystemExit("Refusing to overwrite an existing Relate graph. Back up explicitly and use a new path.")
    with relate.connect(str(STORE)) as db:
        add_node(db,"Device",obj["device"])
        for cap in obj["capabilities"]:add_node(db,"Capability",cap)
        ids={t["id"] for t in obj["tasks"]}
        for task in obj["tasks"]:
            add_node(db,"Task",{k:v for k,v in task.items() if k!="depends"})
            approval_id="approval-"+task["id"]
            add_node(db,"Approval",{"id":approval_id,"decision":"approved" if task["approval"] else "not-approved"})
            attach(db,"Task",task["id"],"AUTHORIZED_BY","Approval",approval_id)
            attach(db,"Task",task["id"],"RUNS_ON","Device",obj["device"]["id"])
            attach(db,"Task",task["id"],"REQUIRES","Capability",task["requires"])
        for task in obj["tasks"]:
            for dep in task["depends"]:
                if dep in ids:
                    attach(db,"Task",task["id"],"DEPENDS_ON","Task",dep)
                else:
                    # Preserve missing-edge evidence as a node with an explicit missing status, not a fake success.
                    missing_id="missing-"+dep
                    if missing_id not in ids:
                        add_node(db,"Evidence",{"id":missing_id,"kind":"missing-reference","digest":dep})
                        ids.add(missing_id)
                    attach(db,"Task",task["id"],"PROVES","Evidence",missing_id)
    print(json.dumps({"file":str(STORE),"size_bytes":STORE.stat().st_size,"nodes_expected":1+len(obj["capabilities"])+len(obj["tasks"])*2+1,"tasks":len(obj["tasks"]),"source":"synthetic fixture","relate":relate.__version__},indent=2))
if __name__=="__main__":main()

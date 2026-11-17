#!/usr/bin/env python3
"""Local-only JSON API to the actual Relate 1.0.1 engine, synthetic dataset, read-only.

Run only behind an HTTPS reverse proxy. No raw Cypher, SQL, file path, URL or arbitrary
code is accepted from the web. Every request opens the same immutable synthetic store
in read-only mode. No tokens, cookies, login or device access.
"""
from __future__ import annotations
import json
import os
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit
from engine import snapshot, task_detail

class Handler(BaseHTTPRequestHandler):
    server_version = "CereX-Judge-Relate/0.1"
    def do_HEAD(self): self.route(False)
    def do_GET(self): self.route(True)
    def do_POST(self): self.error(405, "Read-only API")
    def do_PUT(self): self.error(405, "Read-only API")
    def do_DELETE(self): self.error(405, "Read-only API")
    def do_OPTIONS(self): self.error(405, "Read-only API")
    def error(self, code, message):
        self.send_json(code, {"error":message})
    def route(self, include_body):
        path=urlsplit(self.path).path
        if len(path)>100: return self.error(414,"URI too long")
        try:
            if path in ("/", "/health"):
                data={"status":"ok","engine":"Relate 1.0.1","mode":"synthetic read-only","writes":False}
            elif path=="/graph":
                data=snapshot()
            elif re.fullmatch(r"/task/T-(0[1-8])",path):
                data=task_detail(path.split("/")[-1])
                if not data:return self.error(404,"Unknown task")
            else:
                return self.error(404,"Not found")
        except Exception:
            self.log_error("Graph read failed")
            return self.error(503,"Relate read failure")
        self.send_json(200,data,include_body)
    def send_json(self,code,data,include_body=True):
        data_bytes=json.dumps(data,ensure_ascii=True,separators=(",",":"),sort_keys=True).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Content-Length",str(len(data_bytes)))
        self.send_header("Cache-Control","no-store")
        self.send_header("X-Content-Type-Options","nosniff")
        self.send_header("Referrer-Policy","no-referrer")
        self.send_header("Access-Control-Allow-Origin","null")
        self.send_header("Content-Security-Policy","default-src 'none'")
        self.end_headers()
        if include_body:self.wfile.write(data_bytes)
    def log_message(self, format, *args):
        # No request bodies; URLs only; avoid logs of client IP by default.
        return

if __name__=="__main__":
    port=int(os.environ.get("CEREX_JUDGE_RELATE_PORT","18941"))
    if not (1024<=port<=65535): raise SystemExit("Invalid port")
    service=ThreadingHTTPServer(("127.0.0.1",port),Handler)
    print("CereX judge Relate API on localhost:"+str(port),flush=True)
    service.serve_forever(poll_interval=.4)

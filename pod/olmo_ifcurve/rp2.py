#!/usr/bin/env python3
"""Minimal RunPod REST API v2 client (https://api.runpod.io/v2), standard library only (run olmo-ifcurve).

Written 2026-11-21 because RunPod retired REST API v1 (rest.runpod.io) on 2026-11-15 and the host's runpodctl 2.14.0
still calls it: `podnew` / `podrm` / `killswitch` / `podls` and the budget / balance watchdogs cannot create, list or
delete pods. The API key is read from ~/.runpod/config.toml (apikey = ...) or RUNPOD_API_KEY and never printed.

  rp2.py create <name> --gpu "NVIDIA H200" [--count 1] [--cloud COMMUNITY|SECURE] [--disk 60] [--volume 200]
                [--min-cuda 12.8] [--template uhf9wr47j6]       -> the created pod (JSON)
  rp2.py get <id>                                               -> {id, name, status, cost, host, port} (JSON)
  rp2.py list                                                   -> one line per pod: id name status cost
  rp2.py delete <id>                                            -> HTTP status (204 deleted, 404 gone)
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request

BASE = "https://api.runpod.io/v2"


def key():
    k = os.environ.get("RUNPOD_API_KEY")
    if k:
        return k
    for ln in open(os.path.expanduser("~/.runpod/config.toml")):
        m = re.match(r"\s*apikey\s*=\s*['\"]?([^'\"\s]+)", ln, re.I)
        if m:
            return m.group(1)
    sys.exit("no API key")


def call(method, path, body=None):
    req = urllib.request.Request(BASE + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": f"Bearer {key()}", "Content-Type": "application/json",
                                          "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            txt = r.read().decode()
            return r.status, (json.loads(txt) if txt.strip() else None)
    except urllib.error.HTTPError as e:
        txt = e.read().decode(errors="replace")
        try:
            return e.code, json.loads(txt)
        except json.JSONDecodeError:
            return e.code, {"error": txt[:500]}


def summary(p):
    ssh = (p or {}).get("ssh") or {}
    d = ssh.get("direct") or {}
    return {"id": p.get("id"), "name": p.get("name"), "status": p.get("status"), "cost": p.get("cost"),
            "dataCenterId": p.get("dataCenterId"), "host": d.get("host"), "port": d.get("port"),
            "gpu": (p.get("gpu") or {}).get("id"), "gpu_count": (p.get("gpu") or {}).get("count")}


def main():
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    cmd = a[0]

    def opt(name, default=None):
        return a[a.index(name) + 1] if name in a else default
    if cmd == "create":
        gpu = {"id": opt("--gpu", "NVIDIA H200"), "count": int(opt("--count", "1"))}
        if opt("--min-cuda"):
            gpu["minCudaVersion"] = opt("--min-cuda")
        body = {"name": a[1], "cloud": opt("--cloud", "COMMUNITY"), "gpu": gpu, "disk": int(opt("--disk", "60")),
                "mounts": {"persistent": {"size": int(opt("--volume", "200")), "path": "/workspace"}},
                "templateId": opt("--template", "uhf9wr47j6"), "startSsh": True, "ports": ["22/tcp"]}
        st, r = call("POST", "/pods", body)
        print(json.dumps({"http": st, **(summary(r) if st in (200, 201, 202) and isinstance(r, dict) else {"error": r})}))
        sys.exit(0 if st in (200, 201, 202) else 1)
    if cmd == "get":
        st, r = call("GET", f"/pods/{a[1]}")
        print(json.dumps({"http": st, **(summary(r) if st == 200 else {"error": r})}))
        sys.exit(0 if st == 200 else 1)
    if cmd == "list":
        cur, n = None, 0
        while True:
            st, r = call("GET", "/pods" + (f"?cursor={cur}" if cur else ""))
            if st != 200:
                print(f"LIST_FAIL http {st} {str(r)[:200]}")
                sys.exit(1)
            items = (r.get("pods") or r.get("data")) if isinstance(r, dict) else r
            for p in items or []:
                s = summary(p)
                print(s["id"], s["name"], s["status"], s["cost"])
                n += 1
            cur = (r.get("pagination") or {}).get("nextCursor") if isinstance(r, dict) else None
            if not cur:
                break
        sys.exit(0)
    if cmd == "delete":
        st, r = call("DELETE", f"/pods/{a[1]}")
        print(st if st in (204, 404) else f"{st} {str(r)[:300]}")
        sys.exit(0 if st in (204, 404) else 1)
    sys.exit(__doc__)


if __name__ == "__main__":
    main()

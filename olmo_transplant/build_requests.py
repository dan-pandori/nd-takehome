#!/usr/bin/env python3
"""Build the sampler's request files from the trace manifest (run olmo-transplant; pre-registration
preregistration/olmo-transplant.md, Conditions). VPS-side, torch-free.

For writer w in {dpo, s2300} and set s in {reach, calib}, artifacts/olmo_transplant/requests/<w>_<s>.jsonl.gz holds one
row per request: rid, pid, group, cond, writer, trace, src (stored sample: job|pid|chunk|i), cut, n, prefix (base64
int32: the assistant-side ids after the template's `<think>`), prefix_len.
  rl trace   -> full (T1 if w = dpo, T2 if w = s2300): ids[:think_k], the stored ids through `</think>`;
                B(N) for N in CUTS with c = think_k - 3 > N: ids[:N] + closing;
                P: ids[:draft_k] + closing, when the final answer's opening appears in the thinking.
  dpo trace  -> full (T4 if w = dpo, T3 if w = s2300): ids[:think_k].
  per prompt -> T0: 4 requests, prefix = closing after `<think>`.
closing = [198 '\\n' if the last kept token does not end in a newline] + 524 '</' 27963 'think' 1363 '>\\n\\n'.
All requests on one trace form one group (the sampler warms the prefix cache on the group's longest prefix). Groups
are ordered round-robin over prompts (rank-0 traces of every prompt first), rl before dpo, T0 last.
Every prefix is checked against the stored ids here, and the full prefixes against traces.csv's prefix_sha256.
Usage: build_requests.py <set>"""
import base64
import collections
import csv
import gzip
import hashlib
import json
import os
import sys

import numpy as np

sys.path.insert(0, "olmo_transplant")
from tok import Tok, ids_of  # noqa: E402

S = "artifacts/olmo_transplant/src"
OUT = "artifacts/olmo_transplant/requests"
CUTS = [16384, 8192, 4096, 2048, 1024]
CLOSE = [524, 27963, 1363]
NL = 198
N_SAMPLES = 8
T0_REQUESTS = 4
WRITERS = {"dpo": {"rl": "T1", "dpo": "T4"}, "s2300": {"rl": "T2", "dpo": "T3"}}


def b64(ids):
    return base64.b64encode(np.asarray(ids, dtype=np.int32).tobytes()).decode()


def closing(tok, last_id):
    return ([] if tok.piece[last_id].endswith(b"\n") else [NL]) + CLOSE


def main():
    st = sys.argv[1]
    tok = Tok()
    traces = [t for t in csv.DictReader(open("olmo_transplant/traces.csv")) if t["set"] == st]
    prompts = [p["pid"] for p in csv.DictReader(open("olmo_transplant/prompts.csv")) if p["set"] == st]
    keys = {(t["job"], t["pid"], int(t["chunk"]), int(t["i"])) for t in traces}
    stored = {}
    for job in sorted({k[0] for k in keys}):
        for ln in gzip.open(f"{S}/{job}.jsonl.gz", "rt"):
            r = json.loads(ln)
            k = (job, r["pid"], r["chunk"], r["i"])
            if k in keys:
                stored[k] = ids_of(r)
    os.makedirs(OUT, exist_ok=True)
    traces.sort(key=lambda t: (t["kind"] != "rl", int(t["rank"]), int(t["pid"].split("_")[1])))
    last_tok_after_think = 29  # '>' of the template's '<think>' (does not end in a newline)
    for w, cond in WRITERS.items():
        rows = []
        for t in traces:
            ids = stored[(t["job"], t["pid"], int(t["chunk"]), int(t["i"]))]
            k, c = int(t["think_k"]), int(t["c"])
            full = ids[:k]
            assert hashlib.sha256(json.dumps(full).encode()).hexdigest() == t["prefix_sha256"]
            assert hashlib.sha256(json.dumps(ids).encode()).hexdigest() == t["ids_sha256"]
            src = f"{t['job']}|{t['pid']}|{t['chunk']}|{t['i']}"
            base = {"pid": t["pid"], "group": t["trace"], "writer": w, "trace": t["trace"], "src": src, "n": N_SAMPLES}
            rows.append({**base, "rid": f"{t['trace']}|full", "cond": cond[t["kind"]], "cut": "full",
                         "prefix": b64(full), "prefix_len": len(full)})
            if t["kind"] != "rl":
                continue
            for N in CUTS:
                if c > N:
                    p = ids[:N] + closing(tok, ids[N - 1])
                    rows.append({**base, "rid": f"{t['trace']}|B{N}", "cond": "B", "cut": N, "prefix": b64(p),
                                 "prefix_len": len(p)})
            if t["draft_k"]:
                d = int(t["draft_k"])
                p = ids[:d] + (closing(tok, ids[d - 1]) if d > 0 else [NL] + CLOSE)
                rows.append({**base, "rid": f"{t['trace']}|P", "cond": "P", "cut": "P", "prefix": b64(p),
                             "prefix_len": len(p), "draft_k": d})
        t0 = [NL] + CLOSE if not tok.piece[last_tok_after_think].endswith(b"\n") else CLOSE
        for pid in sorted(prompts, key=lambda p: int(p.split("_")[1])):
            for j in range(T0_REQUESTS):
                rows.append({"pid": pid, "group": f"{pid}|T0", "writer": w, "trace": "", "src": "", "n": N_SAMPLES,
                             "rid": f"{pid}|T0|{j}", "cond": "T0", "cut": 0, "prefix": b64(t0), "prefix_len": len(t0)})
        # check every prefix against the stored ids once more: kept part = stored ids, then exactly the closing
        tk = {t["trace"]: int(t["think_k"]) for t in traces}
        for r in rows:
            p = np.frombuffer(base64.b64decode(r["prefix"]), dtype=np.int32).tolist()
            if not r["src"]:
                assert p == t0, r["rid"]
                continue
            job, pid, ch, i = r["src"].split("|")
            ids = stored[(job, pid, int(ch), int(i))]
            if r["cut"] == "full":
                assert p == ids[:tk[r["trace"]]], r["rid"]
            else:
                n = r["cut"] if r["cut"] != "P" else r["draft_k"]
                assert p[:n] == ids[:n] and p[n:] == (closing(tok, ids[n - 1]) if n > 0 else [NL] + CLOSE), r["rid"]
        f = f"{OUT}/{w}_{st}.jsonl.gz"
        with gzip.open(f, "wt") as g:
            for r in rows:
                g.write(json.dumps(r) + "\n")
        c = collections.Counter(r["cond"] for r in rows)
        print(f, len(rows), "requests", dict(c), "samples", sum(r["n"] for r in rows),
              "prefix tokens", sum(r["prefix_len"] for r in rows), "groups", len({r["group"] for r in rows}))


if __name__ == "__main__":
    main()

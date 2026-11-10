#!/usr/bin/env python3
"""Request files of the optional LoRA arm (run olmo-answeronly; pre-registration, Optional arm). VPS-side, torch-free.

  L1  writer lora_main; thinking = s2300's reach traces, full: prefix = ids[:think_k] (T1's input exactly)
      -> requests/lora_main_l1.jsonl.gz (115 requests x 8)
  L2  writer dpo;       thinking = lora_main's own Leval_main draws with final_label genuine in olmo_ifladder/handcheck.csv,
      up to 4 per reach-41 prompt in a seeded order (random.Random(f"20261110|{pid}")); prefix = the stored ids through
      the first `</think>` (the token completing it must end exactly at the marker plus its newline(s))
      -> requests/dpo_lrev.jsonl.gz
  L3  writer lora_main; the same traces as L2 (self control) -> requests/lora_main_l3.jsonl.gz
Writes olmo_answeronly/lora_traces.csv (L2 / L3 trace manifest: trace, pid, src, think_k, ids sha256, prefix sha256).
Usage: build_lora_requests.py"""
import base64
import csv
import gzip
import hashlib
import json
import random
import sys

import numpy as np

sys.path.insert(0, "olmo_transplant")
sys.path.insert(0, "olmo_answeronly")
from tok import Tok, ids_of, think_end  # noqa: E402
from build_requests import b64, load_stored, unb64, OUT, S, N_SAMPLES  # noqa: E402


def write(name, rows):
    with gzip.open(f"{OUT}/{name}.jsonl.gz", "wt") as g:
        for r in rows:
            g.write(json.dumps(r) + "\n")
    print(name, len(rows), "requests", sum(r["n"] for r in rows), "samples", sum(r["prefix_len"] for r in rows),
          "prefix tokens", len({r["pid"] for r in rows}), "prompts")


def main():
    tok = Tok()
    reach = [p["pid"] for p in csv.DictReader(open("olmo_transplant/prompts.csv")) if p["set"] == "reach"]
    traces = [t for t in csv.DictReader(open("olmo_transplant/traces.csv")) if t["set"] == "reach" and t["kind"] == "rl"]
    stored = load_stored(traces)
    traces.sort(key=lambda t: (int(t["rank"]), int(t["pid"].split("_")[1])))
    l1 = []
    for t in traces:
        ids = stored[(t["job"], t["pid"], int(t["chunk"]), int(t["i"]))]
        full = ids[:int(t["think_k"])]
        assert hashlib.sha256(json.dumps(full).encode()).hexdigest() == t["prefix_sha256"]
        l1.append({"pid": t["pid"], "writer": "lora_main", "trace": t["trace"], "n": N_SAMPLES, "cut": "full",
                   "src": f"{t['job']}|{t['pid']}|{t['chunk']}|{t['i']}", "user_suffix": "", "answer_prefill_k": 0,
                   "rid": f"{t['trace']}|L1", "group": f"{t['trace']}|L1", "cond": "L1", "prefix": b64(full),
                   "prefix_len": len(full)})
    write("lora_main_l1", l1)

    gen = {}
    for r in csv.DictReader(open("olmo_ifladder/handcheck.csv")):
        if r["job"] == "Leval_main" and r["final_label"] == "genuine" and r["pid"] in reach:
            gen[(r["pid"], int(r["chunk"]), int(r["i"]))] = r["item"]
    rows = {}
    for ln in gzip.open(f"{S}/Leval_main.jsonl.gz", "rt"):
        r = json.loads(ln)
        k = (r["pid"], r["chunk"], r["i"])
        if k in gen:
            rows[k] = r
    assert len(rows) == len(gen), (len(rows), len(gen))
    man, l2, l3 = [], [], []
    for pid in sorted({k[0] for k in rows}, key=lambda p: int(p.split("_")[1])):
        ks = sorted(k for k in rows if k[0] == pid)
        random.Random(f"20261110|{pid}").shuffle(ks)
        for rank, k in enumerate(ks[:4]):
            r = rows[k]
            ids = ids_of(r)
            te = think_end(tok, ids)
            assert te and te[2] in (b"\n\n", b"\n"), (k, te)
            kk = te[0]
            pre = ids[:kk]
            assert tok.decode(pre).endswith("</think>" + te[2].decode())
            tr = f"{pid}|lv{rank}"
            src = f"Leval_main|{pid}|{k[1]}|{k[2]}"
            man.append({"trace": tr, "pid": pid, "rank": rank, "src": src, "item": gen[k], "n_tok": len(ids),
                        "think_k": kk, "ids_sha256": hashlib.sha256(json.dumps(ids).encode()).hexdigest(),
                        "prefix_sha256": hashlib.sha256(json.dumps(pre).encode()).hexdigest()})
            for w, c, lst in (("dpo", "L2", l2), ("lora_main", "L3", l3)):
                lst.append({"pid": pid, "writer": w, "trace": tr, "n": N_SAMPLES, "cut": "full", "src": src,
                            "user_suffix": "", "answer_prefill_k": 0, "rid": f"{tr}|{c}", "group": f"{tr}|{c}",
                            "cond": c, "prefix": b64(pre), "prefix_len": len(pre)})
    order = lambda r: (int(r["trace"].rsplit("lv", 1)[1]), int(r["pid"].split("_")[1]))  # noqa: E731
    l2.sort(key=order)
    l3.sort(key=order)
    write("dpo_lrev", l2)
    write("lora_main_l3", l3)
    with open("olmo_answeronly/lora_traces.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(man[0].keys()))
        w.writeheader()
        w.writerows(man)
    print("lora traces", len(man), "prompts", len({m["pid"] for m in man}))


if __name__ == "__main__":
    main()

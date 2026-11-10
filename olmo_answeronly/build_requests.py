#!/usr/bin/env python3
"""Build the sampler's request files for run olmo-answeronly (pre-registration preregistration/olmo-answeronly.md,
Conditions). VPS-side, torch-free. olmo_transplant/build_requests.py's scheme, with the four registered changes to the
full transplant (T1 / T2: prompt + the stored thinking ids[:think_k], through `</think>`):

  A1  user turn + "\\n\\n" + wordings.A1 (row field user_suffix);  prefix = ids[:think_k]
  A2  user turn + "\\n\\n" + wordings.A2;                          prefix = ids[:think_k]
  A3  prefix = ids[:c] + wordings.A3_IDS + ids[c:think_k]   (c = think_k - 3: the sentence on its own line just before
      the stored `</` `think` `>\\n\\n`)
  A4  prefix = ids[:think_k] + ids[think_k:think_k + kp]    (the first kp stored ids of the trace's own final answer,
      kp = min(5, answer tokens - 1): never the whole answer; 5 traces have answers of 4-5 tokens before EOS;
      row field answer_prefill_k = kp: the sampler writes text = decode(prefill + generated))

Only `rl` traces of olmo_transplant/traces.csv (reach 115, calibration 36). Groups: A1 and A2 have their own user turn,
so each is its own group (trace|A1, trace|A2); A3 and A4 share ids[:c] and form one group (trace|A34). Groups are
ordered by (trace rank, prompt number), as olmo-transplant. Every prefix is re-checked against the stored ids here.
Usage: build_requests.py <reach|calib> [--writers dpo,s2300]"""
import argparse
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
sys.path.insert(0, "olmo_answeronly")
from tok import Tok, ids_of  # noqa: E402
import wordings as W  # noqa: E402

S = "artifacts/olmo_answeronly/inputs"
OUT = "artifacts/olmo_answeronly/requests"
CLOSE = [524, 27963]  # `</` `think`; the third token (1363 '>\n\n' or 397 '>\n') is the stored one
N_SAMPLES = 8


def b64(ids):
    return base64.b64encode(np.asarray(ids, dtype=np.int32).tobytes()).decode()


def unb64(s):
    return np.frombuffer(base64.b64decode(s), dtype=np.int32).tolist()


def load_stored(traces):
    keys = {(t["job"], t["pid"], int(t["chunk"]), int(t["i"])) for t in traces}
    stored = {}
    for job in sorted({k[0] for k in keys}):
        for ln in gzip.open(f"{S}/{job}.jsonl.gz", "rt"):
            r = json.loads(ln)
            k = (job, r["pid"], r["chunk"], r["i"])
            if k in keys:
                stored[k] = ids_of(r)
    return stored


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("set", choices=["reach", "calib"])
    ap.add_argument("--writers", default="dpo,s2300")
    a = ap.parse_args()
    tok = Tok()
    traces = [t for t in csv.DictReader(open("olmo_transplant/traces.csv")) if t["set"] == a.set and t["kind"] == "rl"]
    stored = load_stored(traces)
    traces.sort(key=lambda t: (int(t["rank"]), int(t["pid"].split("_")[1])))
    os.makedirs(OUT, exist_ok=True)
    assert tok.decode(W.A3_IDS) == W.A3_TEXT
    for w in a.writers.split(","):
        rows = []
        for t in traces:
            ids = stored[(t["job"], t["pid"], int(t["chunk"]), int(t["i"]))]
            k, c = int(t["think_k"]), int(t["c"])
            assert c == k - 3 and ids[c:c + 2] == CLOSE and ids[k - 1] == int(t["close_tok"])
            assert tok.piece[ids[c - 1]].endswith(b"\n")
            full = ids[:k]
            assert hashlib.sha256(json.dumps(full).encode()).hexdigest() == t["prefix_sha256"]
            assert hashlib.sha256(json.dumps(ids).encode()).hexdigest() == t["ids_sha256"]
            ans = [i for i in ids[k:] if i not in tok.special]
            assert ids[k:k + len(ans)] == ans, t["trace"]  # specials (EOS) only at the end
            kp = min(W.A4_K, len(ans) - 1)  # never the whole answer (5 traces have 5 or fewer answer tokens)
            pre = ans[:kp]
            src = f"{t['job']}|{t['pid']}|{t['chunk']}|{t['i']}"
            base = {"pid": t["pid"], "writer": w, "trace": t["trace"], "src": src, "n": N_SAMPLES, "cut": "full",
                    "user_suffix": "", "answer_prefill_k": 0}
            for cond, grp, prefix, extra in [
                ("A1", "A1", full, {"user_suffix": W.USER_SUFFIX["A1"]}),
                ("A2", "A2", full, {"user_suffix": W.USER_SUFFIX["A2"]}),
                ("A3", "A34", ids[:c] + W.A3_IDS + ids[c:k], {}),
                ("A4", "A34", full + pre, {"answer_prefill_k": kp}),
            ]:
                rows.append({**base, **extra, "rid": f"{t['trace']}|{cond}", "group": f"{t['trace']}|{grp}",
                             "cond": cond, "prefix": b64(prefix), "prefix_len": len(prefix)})
        # re-check every prefix: stored ids plus exactly the registered change
        for r in rows:
            job, pid, ch, i = r["src"].split("|")
            ids = stored[(job, pid, int(ch), int(i))]
            tt = next(t for t in traces if t["trace"] == r["trace"])
            k = int(tt["think_k"])
            p = unb64(r["prefix"])
            exp = {"A1": ids[:k], "A2": ids[:k], "A3": ids[:k - 3] + W.A3_IDS + ids[k - 3:k],
                   "A4": ids[:k + r["answer_prefill_k"]]}[r["cond"]]
            assert (r["answer_prefill_k"] > 0) == (r["cond"] == "A4") and r["answer_prefill_k"] <= W.A4_K
            assert p == exp, r["rid"]
            assert (r["user_suffix"] != "") == (r["cond"] in ("A1", "A2"))
            assert r["user_suffix"] in ("", W.USER_SUFFIX.get(r["cond"], ""))
        f = f"{OUT}/{w}_{a.set}.jsonl.gz"
        with gzip.open(f, "wt") as g:
            for r in rows:
                g.write(json.dumps(r) + "\n")
        cnt = collections.Counter(r["cond"] for r in rows)
        print(f, len(rows), "requests", dict(cnt), "samples", sum(r["n"] for r in rows),
              "prefix tokens", sum(r["prefix_len"] for r in rows), "groups", len({r["group"] for r in rows}))


if __name__ == "__main__":
    main()

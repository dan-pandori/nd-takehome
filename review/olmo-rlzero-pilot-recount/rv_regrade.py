#!/usr/bin/env python3
"""Re-grade every stored sample text with the upstream verifier (rl = worker thread, main = main thread) and my own
integer read-out; re-decode the stored token ids with the Olmo tokenizer (skip_special_tokens=True) and compare with
the stored text; compare everything with the executor's graded rows (pid, chunk, i, n_tok, finish, rl, main).

Usage: rv_regrade.py <job> [<job> ...]     -> out/regrade_<job>.jsonl (one row per sample, no text) + a summary line
"""
import json
import sys
import time

import rv_core as R


def main():
    from tokenizers import Tokenizer
    tok = Tokenizer.from_file(str(R.Path.home() / "review/olmo-rlzero-pilot-rv/tok/base/tokenizer.json"))
    probs = R.problems()
    for job in sys.argv[1:]:
        t0 = time.time()
        g = R.graded(job)
        gk = {(r["pid"], r["chunk"], r["i"]): r for r in g} if g is not None else {}
        rows, mism = [], {"missing_in_graded": 0, "n_tok": 0, "finish": 0, "rl": 0, "main": 0, "decode": 0,
                          "len_ids": 0, "dup_key": 0}
        seen = set()
        batch = []
        for s in R.samples(job):
            k = (s["pid"], s["chunk"], s["i"])
            if k in seen:
                mism["dup_key"] += 1
            seen.add(k)
            ids = R.ids_of(s)
            dec = tok.decode(ids, skip_special_tokens=True)
            batch.append((s, k, ids, dec))
        preds = [(s["text"], str(probs[s["pid"]]["answer"])) for s, _, _, _ in batch]
        rl = R.grade_rl_many(preds) if preds else []
        for (s, k, ids, dec), r_rl in zip(batch, rl):
            lab = str(probs[s["pid"]]["answer"])
            r_main = R.grade_main(s["text"], lab)
            mi = R.my_int(s["text"])
            row = {"job": job, "pid": s["pid"], "model": s["model"], "chunk": s["chunk"], "i": s["i"],
                   "n_tok": s["n_tok"], "finish": s["finish"], "rl": bool(r_rl), "main": bool(r_main),
                   "my_int": mi, "my_int_ok": (mi is not None and mi == int(lab)) if R.re.fullmatch(r"-?\d+", lab.strip()) else None,
                   "decode_ok": dec == s["text"], "len_ids_ok": len(ids) == s["n_tok"],
                   "last_id": ids[-1] if ids else None}
            mism["decode"] += not row["decode_ok"]
            mism["len_ids"] += not row["len_ids_ok"]
            e = gk.get(k)
            if g is not None:
                if e is None:
                    mism["missing_in_graded"] += 1
                else:
                    mism["n_tok"] += e["n_tok"] != s["n_tok"]
                    mism["finish"] += e["finish"] != s["finish"]
                    mism["rl"] += bool(e["rl"]) != row["rl"]
                    mism["main"] += bool(e.get("main")) != row["main"]
                    row["ex_rl"], row["ex_main"], row["ex_ansline"] = bool(e["rl"]), bool(e.get("main")), e.get("ansline")
            rows.append(row)
        extra_graded = len(set(gk) - seen) if g is not None else None
        with open(R.OUT / f"regrade_{job}.jsonl", "w") as f:
            for row in rows:
                f.write(json.dumps(row) + "\n")
        summ = {"job": job, "samples": len(rows), "graded_rows": len(g) if g is not None else None,
                "graded_not_in_samples": extra_graded, "mismatch": mism,
                "rl_correct": sum(r["rl"] for r in rows), "main_correct": sum(r["main"] for r in rows),
                "my_int_correct": sum(bool(r["my_int_ok"]) for r in rows), "secs": round(time.time() - t0, 1)}
        print(json.dumps(summ), flush=True)
        with open(R.OUT / "regrade_summary.jsonl", "a") as f:
            f.write(json.dumps(summ) + "\n")


if __name__ == "__main__":
    main()

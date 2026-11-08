"""My re-grade vs the executor's graded rows (artifacts/olmo_rlzero_if/graded/<job>.jsonl), row by row on
(pid, chunk, i); and the stored-ids integrity summary from my re-grade (decode == text, n_tok == len(ids), cut iff
len == cap, EOS ending, tag-token counts). Output: out/gradecmp.txt, out/decode_check.txt"""
import json
import os
from collections import Counter

import rv_core as C


def main():
    lines, dl = [], []
    tot = Counter()
    for fn in sorted(os.listdir(os.path.join(C.OUT, "regrade"))):
        if not fn.endswith(".jsonl"):
            continue
        job = fn[:-6]
        mine = {(r["pid"], r["chunk"], r["i"]): r for r in map(json.loads, open(os.path.join(C.OUT, "regrade", fn)))}
        gpath = os.path.join(C.ART, "graded", f"{job}.jsonl")
        theirs = {}
        if os.path.exists(gpath):
            theirs = {(r["pid"], r["chunk"], r["i"]): r for r in map(json.loads, open(gpath))}
        c = Counter()
        ex = []
        for k, m in mine.items():
            t = theirs.get(k)
            if t is None:
                c["missing_theirs"] += 1
                continue
            if m["task"] not in ("ifbench", "ifeval"):
                continue
            c["rows"] += 1
            for f in ("strict", "loose", "per"):
                if m[f] != t.get(f):
                    c[f"diff_{f}"] += 1
                    if len(ex) < 5:
                        ex.append((f, k, m[f], t.get(f), m.get("random_dep"), m.get("redacted")))
            if m["think_end"] != t.get("think_end"):
                c["diff_think_end"] += 1
            if m.get("t1") != t.get("t1"):
                c["diff_t1"] += 1
            if m.get("cont") != t.get("cont"):
                c["diff_cont"] += 1
            c["strict"] += m["strict"]
        c["extra_theirs"] = len(set(theirs) - set(mine))
        tot.update(c)
        lines.append(f"{job:14s} " + " ".join(f"{a}={b}" for a, b in sorted(c.items())))
        for e in ex:
            lines.append(f"    {e}")
        d = Counter()
        for m in mine.values():
            d["rows"] += 1
            d["dec_eq"] += m["dec_eq"] is True
            d["redacted"] += m["dec_eq"] is None
            d["ntok_eq_ids"] += m["n_tok"] == m["n_ids"] or m["dec_eq"] is None
            d["cut"] += m["finish"] == "length"
            d["cut_iff_cap"] += (m["finish"] == "length") == m["len_cap"] or m["dec_eq"] is None
            d["eos_end"] += m["eos_end"]
            d["finish_stop"] += m["finish"] == "stop"
            d["stop_answer"] += m["stop_reason"] == "</answer>"
            d["think_open_ids"] += m["n_think_open"] > 0
            d["think_close_ids"] += m["n_think_close"] > 0
            d["think_end_text"] += m["think_end"]
            d["ans_open_ids"] += m["n_ans_open"] > 0
            d["ans_close_ids"] += m["n_ans_close"] > 0
            d["turn_tokens"] += m["n_turn"] > 0
        dl.append(f"{job:14s} " + " ".join(f"{a}={b}" for a, b in d.items()))
    lines.append("TOTAL " + " ".join(f"{a}={b}" for a, b in sorted(tot.items())))
    open(os.path.join(C.OUT, "gradecmp.txt"), "w").write("\n".join(lines) + "\n")
    open(os.path.join(C.OUT, "decode_check.txt"), "w").write("\n".join(dl) + "\n")
    print("\n".join(lines))
    print("\n".join(dl))


if __name__ == "__main__":
    main()

"""Row-by-row comparison of my re-grade (out/regrade/) with the executor's graded rows (artifacts/olmo_ifomega/graded/),
joined on (job, pid, chunk, i). Reports, per job and field, rows compared / disagreeing, and lists every disagreement.
Fields: IF strict, loose, rlview, per; OMEGA omega, rl, doubly, omega_ans; both: n_tok, finish, think_end.
Output: out/gradecmp.json, out/gradecmp.txt"""
import json
import os
from collections import Counter, defaultdict

import rv_core as C


def main():
    rep, txt = {}, []
    tot = Counter()
    dis_all = []
    for job in C.jobs():
        mine = {(r["pid"], r["chunk"], r["i"]): r for r in C.load_regrade(job)}
        fn = os.path.join(C.ART, "graded", f"{job}.jsonl")
        theirs = {}
        for ln in open(fn):
            r = json.loads(ln)
            theirs[(r["pid"], r["chunk"], r["i"])] = r
        only_m = set(mine) - set(theirs)
        only_t = set(theirs) - set(mine)
        cnt = Counter()
        for k in set(mine) & set(theirs):
            a, b = mine[k], theirs[k]
            if a["task"] in ("omega_out", "omega_in"):
                a = dict(a, doubly=bool(a["omega"] and a["rl"]))
            fields = ["n_tok", "finish", "think_end"]
            if a["task"] in ("ifbench", "ifeval"):
                fields += ["strict", "loose", "rlview", "per"]
            elif a["task"].startswith("omega"):
                fields += ["omega", "rl", "doubly", "omega_ans"]
            for f in fields:
                cnt[f + "_n"] += 1
                if a.get(f) != b.get(f):
                    cnt[f + "_diff"] += 1
                    dis_all.append({"job": job, "key": list(k), "field": f, "mine": a.get(f), "theirs": b.get(f)})
        rep[job] = {"mine": len(mine), "theirs": len(theirs), "only_mine": len(only_m), "only_theirs": len(only_t),
                    **cnt}
        tot.update(cnt)
        diffs = {f: v for f, v in cnt.items() if f.endswith("_diff")}
        txt.append(f"{job:18s} rows mine {len(mine)} theirs {len(theirs)} only_mine {len(only_m)} only_theirs {len(only_t)}"
                   f" diffs {diffs}")
    txt.append("TOTAL " + json.dumps({k: v for k, v in sorted(tot.items())}))
    by_field = defaultdict(list)
    for d in dis_all:
        by_field[d["field"]].append(d)
    for f, lst in by_field.items():
        txt.append(f"-- {f}: {len(lst)} disagreements")
        for d in lst[:40]:
            txt.append("   " + json.dumps(d)[:300])
    json.dump({"per_job": rep, "total": tot, "disagreements": dis_all}, open(os.path.join(C.OUT, "gradecmp.json"), "w"),
              indent=0)
    open(os.path.join(C.OUT, "gradecmp.txt"), "w").write("\n".join(txt) + "\n")
    print("\n".join(txt[-60:]))


if __name__ == "__main__":
    main()

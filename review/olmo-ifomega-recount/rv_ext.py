"""Audit of the defender extension and challenger confirmation against the pre-registered stopping rule, from my cell
draws. Stopping grade: IF strict, OMEGA doubly (omega and rl). For each extended cell: the chunk sequence (job, chunk,
size, successes), the cumulative count, where the rule says to stop (after the chunk in which the count over the
completed prefix reaches 2, prior = fixed-phase successes; hand-gate continuations E2/E3 / C2/C3 flagged), overshoot
(chunks drawn after the stop point within the same job), and the 256 cap. Output: out/ext.txt, out/ext.json"""
import json
import os
from collections import OrderedDict

import rv_core as C
import rv_stats as S


def main():
    cells = S.load()
    out, txt = {}, []
    for (m, p), c in sorted(cells.items(), key=lambda t: (t[1]["task"], t[0][1], t[0][0])):
        if c["role"] == "F":
            continue
        g = "strict" if c["task"].startswith("if") else "doubly"
        fl = c["g"][g]
        chunks = OrderedDict()
        for j, (job, ch, i) in enumerate(c["key"]):
            chunks.setdefault((job, ch), []).append(fl[j])
        seq, cum, stop_at, over, jobs_after_stop = [], 0, None, 0, set()
        nfix = sum(c["fixed"])
        cum = sum(fl[:nfix])
        for (job, ch), v in chunks.items():
            if job.startswith("F_"):
                continue
            seq.append((job, ch, len(v), sum(v)))
        # per job: does the job stop after the first chunk where cumulative >= 2 (inflight 1 jobs)?
        k = cum
        first_reach = None
        for idx, (job, ch, n, s) in enumerate(seq):
            if first_reach is not None:
                over += n
                jobs_after_stop.add(job)
            k += s
            if first_reach is None and k >= 2:
                first_reach = idx
        total = len(fl)
        rec = {"model": m, "task": c["task"], "role": c["role"], "n_fixed": nfix, "fixed_succ": sum(fl[:nfix]),
               "chunks": seq, "total": total, "succ_total": sum(fl), "succ_256": sum(fl[:256]),
               "count_reached_2_at_chunk": first_reach, "drawn_after_count_2": over,
               "jobs_after_count_2": sorted(jobs_after_stop), "over_cap": max(0, total - 256)}
        out[f"{m}|{p}"] = rec
        sizes = sorted({n for _, _, n, _ in seq})
        txt.append(f"{m:5s} {p:70s} {c['role']} fixed {sum(fl[:nfix])}/{nfix} ext chunks {len(seq)} sizes {sizes}"
                   f" total {total} succ {sum(fl)} reach2@{first_reach} after2 {over} {sorted(jobs_after_stop)}"
                   f"{' OVERCAP ' + str(total - 256) if total > 256 else ''}")
    json.dump(out, open(os.path.join(C.OUT, "ext.json"), "w"), indent=0)
    open(os.path.join(C.OUT, "ext.txt"), "w").write("\n".join(txt) + "\n")
    # summaries
    over = [k for k, r in out.items() if r["drawn_after_count_2"] > 0]
    cap = [k for k, r in out.items() if r["over_cap"] > 0]
    print(f"extended cells {len(out)}; with draws after the count reached 2: {len(over)}; over the 256 cap: {len(cap)}")
    for k in over:
        r = out[k]
        print("  after-2:", k, r["drawn_after_count_2"], r["jobs_after_count_2"], "succ", r["succ_total"], "/", r["total"])
    for k in cap:
        print("  overcap:", k, out[k]["total"])


if __name__ == "__main__":
    main()

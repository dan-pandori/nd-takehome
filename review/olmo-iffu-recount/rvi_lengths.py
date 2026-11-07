"""Phase 2: answer lengths without the hint (olmo-ifomega's fixed-phase draws, streamed from the bucket) vs with it
(this run's T2 / T2c draws), for the 48 hinted prompts. Words = whitespace split of the answer (text after the last
'</think>', stripped); per prompt the median, then the median over the 48 prompts (the executor's summary statistic).
-> out/lengths.txt, out/lengths.json
"""
import gzip
import io
import json
import statistics as st
import subprocess

import rvi_core as C

BK = "hf://buckets/dan-pandori/nd-rl/olmo-ifomega/artifacts/olmo_ifomega/samples/"


def words(text):
    a = C.answer_of(text)
    return None if a is None else len(a.split())


def main():
    prov = json.load(open(C.OUT / "provenance.json"))
    hinted = set(prov["t2"] + prov["t2c"]) | {"ifeval_2350", "ifeval_2447", "ifeval_3478", "ifeval_1314",
                                              "ifeval_2247", "ifeval_2563"}
    un = {}
    for name in ("F_dpo_ifb", "F_dpo_ife", "F_s2300_ifb", "F_s2300_ife"):
        p = subprocess.Popen(["hf", "buckets", "cp", BK + name + ".jsonl.gz", "-"], stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL)
        with gzip.open(io.BufferedReader(p.stdout), "rt", encoding="utf-8") as f:
            for ln in f:
                r = json.loads(ln)
                if r["pid"] in hinted:
                    un.setdefault((r["model"], r["pid"]), []).append(words(r["text"]))
        p.wait()
    hi = {}
    for job in ("T2_dpo", "T2_s2300", "T2c_dpo", "T2c_s2300"):
        for r in C.iter_rows(job, with_ids=False):
            hi.setdefault((r["model"], r["pid"]), []).append(words(r["text"]))
    res, lines = {}, []
    for m in ("dpo", "s2300"):
        mu = [st.median([w for w in un[(m, p)] if w is not None]) for p in sorted(hinted)]
        mh = [st.median([w for w in hi[(m, p)] if w is not None]) for p in sorted(hinted)]
        nu = {p: len(un[(m, p)]) for p in hinted}
        res[m] = {"unhinted_median_of_medians": st.median(mu), "hinted_median_of_medians": st.median(mh),
                  "unhinted_draws_per_prompt": sorted(set(nu.values()))}
        lines.append(f"{m}: median over the 48 prompts of the per-prompt median answer words: unhinted "
                     f"{st.median(mu)} (olmo-ifomega fixed phase, {sorted(set(nu.values()))} draws per prompt) -> hinted "
                     f"{st.median(mh)}")
    C.dump(res, "lengths.json")
    (C.OUT / "lengths.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()

"""Extra contamination check: the RL-Zero-IF launch-script snapshot (open-instruct 7e780f2fea) names the pre-release
dataset saurabh5/IF_multi_constraints_upto5_filtered_olmo_completions_filtered (mixer count 13314), not
Dolci-RL-Zero-IF-7B (13,179). Read only its `key` and `messages` columns over HTTP (HfFileSystem row groups) at
3a5ace2c, compare its keys / prompts with Dolci's, and scan every evaluation prompt against all of its user turns with
rv_contam's 8-gram raw containment (content grams: df < 20 over this corpus).
Output: out/contam_pre.txt, ~/review/rzi_rv/contam/pre_matches.json"""
import gzip
import json
import os
from collections import Counter, defaultdict

import pyarrow.parquet as pq
from huggingface_hub import HfFileSystem

import rv_core as C
from rv_contam import grams

REV = "3a5ace2c2a19f30cf7cd0e3e4c1d4310ea568d73"
BASE = f"datasets/saurabh5/IF_multi_constraints_upto5_filtered_olmo_completions_filtered@{REV}/data/"
CACHE = os.path.join(C.BIG, "data", "pre_prompts.jsonl.gz")


def fetch():
    if os.path.exists(CACHE):
        return [json.loads(x) for x in gzip.open(CACHE, "rt")]
    fs = HfFileSystem()
    rows = []
    for i in range(15):
        f = fs.open(BASE + f"train-{i:05d}-of-00015.parquet", "rb", block_size=1 << 20)
        t = pq.ParquetFile(f).read(columns=["key", "messages", "dataset", "avg_score"]).to_pylist()
        for r in t:
            u = "\n".join(m["content"] for m in r["messages"] if m["role"] == "user")
            rows.append({"key": r["key"], "user": u, "dataset": r["dataset"], "avg_score": r["avg_score"],
                         "n_msgs": len(r["messages"]), "file": i})
        print("file", i, len(rows), flush=True)
    with gzip.open(CACHE + ".tmp", "wt") as g:
        for r in rows:
            g.write(json.dumps(r) + "\n")
    os.replace(CACHE + ".tmp", CACHE)
    return rows


def main():
    import pyarrow.parquet as pq2
    pre = fetch()
    dol = pq2.read_table(os.path.join(C.BIG, "data", "dolci_rlzero_if.parquet"), columns=["key", "prompt"]).to_pylist()
    lines = [f"pre-release rows {len(pre)}; distinct keys {len({r['key'] for r in pre})}; Dolci rows {len(dol)}"]
    dk = {r["key"] for r in dol}
    pk = {r["key"] for r in pre}
    lines.append(f"Dolci keys in pre-release: {len(dk & pk)} of {len(dk)}")
    norm = lambda s: " ".join(s.split())
    dp = {norm(r["prompt"][len("user: "):] if r["prompt"].startswith("user: ") else r["prompt"]) for r in dol}
    pp = {norm(r["user"]) for r in pre}
    lines.append(f"Dolci prompts (minus 'user: ') equal to a pre-release user turn: {len(dp & pp)} of {len(dp)}")
    lines.append(f"pre-release first 13314 rows' keys in Dolci: {len({r['key'] for r in pre[:13314]} & dk)}")
    lines.append(f"avg_score of pre-release rows: {Counter(round(r['avg_score'] or -1, 2) for r in pre).most_common(6)}")
    P = C.load_problems()
    EG = {p: grams(r["prompt"]) for p, r in P.items()}
    RG = [grams(r["user"]) for r in pre]
    df = Counter()
    for g in RG:
        df.update(g)
    content = {p: {g for g in gs if df[g] < 20} for p, gs in EG.items()}
    owner = defaultdict(list)
    for p, gs in EG.items():
        for g in gs:
            owner[g].append(p)
    best = defaultdict(lambda: [0.0, 0.0, "", ""])
    matches = defaultdict(list)
    for j, dg in enumerate(RG):
        cnt, ccnt = Counter(), Counter()
        for g in dg:
            for p in owner.get(g, ()):
                cnt[p] += 1
                if g in content[p]:
                    ccnt[p] += 1
        for p, k in cnt.items():
            raw = k / len(EG[p])
            con = ccnt[p] / len(content[p]) if content[p] else 0.0
            b = best[p]
            if raw > b[0]:
                b[0], b[2] = raw, pre[j]["key"]
            if con > b[1]:
                b[1], b[3] = con, pre[j]["key"]
            if con >= 0.3:
                matches[p].append({"key": pre[j]["key"], "raw": round(raw, 4), "con": round(con, 4),
                                   "in_dolci": pre[j]["key"] in dk, "text": pre[j]["user"][:4000]})
    lines.append("eval prompts with content >= 0.3 against the pre-release corpus:")
    for p in sorted(matches):
        b = best[p]
        lines.append(f"  {p}: raw {b[0]:.3f} content {b[1]:.3f} ({b[3]}; in Dolci {b[3] in dk}) "
                     f"n>=0.3 {len(matches[p])}{'  RULE-EXCLUDE' if b[1] >= 0.5 or b[0] >= 0.8 else ''}")
    lines.append("eval prompts with raw >= 0.8: " + str(sorted(p for p, b in best.items() if b[0] >= 0.8)))
    json.dump(matches, open(os.path.join(C.BIG, "contam", "pre_matches.json"), "w"), indent=1)
    open(os.path.join(C.OUT, "contam_pre.txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()

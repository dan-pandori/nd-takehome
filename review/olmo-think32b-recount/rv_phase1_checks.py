"""Ad-hoc phase-1 claim checks (reviewer), saved so every sentence of the recount has a source."""
import collections, glob, gzip, json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_core as C
out = []
# 1. nd_verify imports in the run's code
hits = []
for base in ("olmo32", "pod/olmo32"):
    for f in glob.glob(os.path.join(C.ROOT, base, "**", "*"), recursive=True):
        if os.path.isfile(f) and f.endswith((".py", ".sh")):
            if re.search(r"nd_verify|verify_text", open(f, errors="ignore").read()):
                hits.append(os.path.relpath(f, C.ROOT))
out.append(f"nd_verify / verify_text mentions in olmo32/ and pod/olmo32/: {hits}")
# 2. bucket listing: weights
ls = open(os.path.join(C.HERE, "out", "bucket_ls.txt")).read()
out.append(f"bucket files matching safetensors/.bin/.pt/.gguf: {len(re.findall(r'(safetensors|\.bin\b|\.pt\b|\.gguf)', ls))}")
# 3. Stage 0 rl-only rows: finish and final source
rs = [r for r in C.rows() if r["job"] == "s0_dpo" and r["rl"] != r["final"]]
out.append("Stage 0 rl-only: " + json.dumps(collections.Counter((r["finish"], r["final_src"]) for r in rs).most_common()))
line = [r for r in rs if r["final_src"] == "line"]
out.append(f"  the 'line' case: finish={line[0]['finish']} final_val={line[0]['final_val']} label={line[0]['label']}" if line else "  no line case")
# 4. dpo fixed-phase rl-only reasons (headline set)
head = {p["pid"] for p in C.problems()} - C.excluded()
fx = [r for r in C.rows() if r["job"] == "F_dpo" and r["pid"] in head and r["rl"] and not r["final"]]
out.append("F_dpo rl-only (59 problems): " + json.dumps(collections.Counter((r["finish"], r["final_src"]) for r in fx).most_common()))
for m in ("s0100", "s0750", "s2300"):
    fm = [r for r in C.rows() if r["job"] == f"F_{m}" and r["pid"] in head and r["rl"] and not r["final"]]
    out.append(f"F_{m} rl-only: " + json.dumps(collections.Counter((r["finish"], r["final_src"]) for r in fm).most_common()))
# 5. s0100 and s2300 solved sets (>= 1 of 8, rl)
def solved(m):
    c = collections.Counter(r["pid"] for r in C.rows() if r["job"] == f"F_{m}" and r["pid"] in head and r["rl"])
    return {p for p in c if c[p] > 0}
a, b = solved("s0100"), solved("s2300")
out.append(f"solved>=1/8 (rl): s0100 {len(a)}, s2300 {len(b)}, identical sets: {a == b}, symmetric difference {sorted(a ^ b)}")
# 6. excluded problem cells
ex = collections.defaultdict(lambda: [0, 0])
for r in C.rows():
    if r["job"].startswith("F_") and r["pid"] == "aime2026_01":
        ex[r["model"]][0] += 1; ex[r["model"]][1] += r["rl"]
out.append(f"aime2026_01 (excluded) fixed phase n, rl: {dict(ex)}")
# 7. overshoot per challenger / defender job: chunks after the one where the target was met
E = json.load(open(os.path.join(C.HERE, "out", "ext.json")))
meta = {}
for f in glob.glob(os.path.join(C.ROOT, "artifacts/olmo32/meta/*.json")):
    m = json.loads(open(f).read().strip().splitlines()[-1]); meta[m["job"]] = m
for k, chunks in E.items():
    byjob = collections.OrderedDict()
    for c in chunks:
        if c["job"].startswith("F_"):
            continue
        byjob.setdefault(c["job"], []).append(c)
    for job, cs in byjob.items():
        tgt = meta[job]["stop_after"]; cnt = 0; met = None
        for idx, c in enumerate(cs):
            cnt += c["doubly"]
            if tgt and met is None and cnt >= tgt:
                met = idx
        idxs = [c["chunk"] for c in cs]
        contiguous = idxs == list(range(idxs[0], idxs[0] + len(idxs)))
        out.append(f"{k} {job}: stop_after={tgt} inflight={meta[job]['inflight']} chunks={idxs[0]}..{idxs[-1]} contiguous={contiguous} "
                   f"target met at chunk index {met} -> kept after: {len(cs) - 1 - met if met is not None else 'n/a (ran to its n)'}")
# 8. MANIFEST.jsonl: append-only since the run's base
d = subprocess.run(["git", "-C", "/home/dan/work/olmo-think32b", "diff", "--numstat", "525e2e0e", "HEAD", "--", "artifacts/MANIFEST.jsonl"],
                   capture_output=True, text=True).stdout.strip()
out.append(f"MANIFEST.jsonl numstat (added, deleted) since 525e2e0e: {d}")
d2 = subprocess.run(["git", "-C", "/home/dan/work/olmo-think32b", "diff", "--numstat", "525e2e0e", "HEAD"], capture_output=True, text=True).stdout
dele = [l for l in d2.splitlines() if l.split("\t")[1] not in ("0", "-")]
out.append(f"files with deleted lines since 525e2e0e: {[l.split(chr(9))[2] for l in dele]}")
open(os.path.join(C.HERE, "out", "phase1_checks.txt"), "w").write("\n".join(out) + "\n")
print("\n".join(out))

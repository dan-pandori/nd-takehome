"""Negative / positive controls for rv_regrade (reviewer): wrong labels must credit ~nothing; the true label on texts
the executor marked credited must credit them (already shown by 0 disagreements). Runs on F_s2300 (480 samples)."""
import gzip, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import rv_regrade as R, rv_upstream as U
n = rl_wrong = fin_wrong = rl_true = fin_true = 0
with gzip.open(os.path.join(ROOT, "artifacts/olmo32/samples/F_s2300.jsonl.gz"), "rt") as f:
    for ln in f:
        r = json.loads(ln); lab = R.LABEL[r["pid"]]; wrong = str((int(lab) + 1) % 1000)
        n += 1
        rl_wrong += U.rl_grade(r["text"], wrong)
        v = R.my_final(r["text"])[2]; fin_wrong += (v is not None and v == int(wrong))
        rl_true += U.rl_grade(r["text"], lab); fin_true += (v is not None and v == int(lab))
print(f"F_s2300 n={n}: label+1 -> rl {rl_wrong}, final {fin_wrong}; true label -> rl {rl_true}, final {fin_true}")

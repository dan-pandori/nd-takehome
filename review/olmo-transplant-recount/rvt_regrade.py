"""Re-grade every stored answer of run olmo-transplant, and the olmo-ifomega source samples the traces come from.

Run rows: graded text = '</think>' + sampled text (the inserted prefix always ends in the `</think>` closing).
Source rows (bucket copies in ~/review/otr_rv/src): the stored text. Also checks text == decode(ids) (my piece
table, special tokens skipped) for every row. pid -> upstream key: the problems file's `key` for ifbench_<n>.
Output: out/regrade/<job>.jsonl.gz, one row per sample: key, strict, per, loose, words, decode_ok, has_close.
Usage: rvt_regrade.py run|src
"""
import gzip
import json
import sys
import time

from rvt_core import ART, OUT, RAW, SCR, SRC_JOBS, JOBS, Pieces, answer_of, iter_gz, unb64
from rvt_graders import UPSTREAM, if_grade

PROB = {}
for ln in open(RAW / "olmo_ifomega" / "problems.jsonl"):
    r = json.loads(ln)
    if r["task"] == "ifbench":
        PROB[r["pid"]] = r


def main():
    mode = sys.argv[1]
    pc = Pieces()
    (OUT / "regrade").mkdir(exist_ok=True)
    jobs = JOBS if mode == "run" else SRC_JOBS
    for job in jobs:
        t0 = time.time()
        rep = {}
        path = ART / "samples" / f"{job}.jsonl.gz" if mode == "run" else SCR / "src" / f"{job}.jsonl.gz"
        n = bad_dec = 0
        with gzip.open(OUT / "regrade" / f"{job}.jsonl.gz", "wt") as g:
            for r in iter_gz(path, rep):
                pid = r["pid"]
                if not pid.startswith("ifbench_"):
                    continue
                rec = UPSTREAM[str(PROB[pid]["key"])]
                ids = unb64(r["ids"])
                dec_ok = pc.text(ids) == r["text"]
                bad_dec += not dec_ok
                if mode == "run":
                    full = "</think>" + r["text"]
                    key = f"{job}|{r['rid']}|{r['i']}"
                else:
                    full = r["text"]
                    key = f"{job}|{pid}|{r['chunk']}|{r['i']}"
                ans = answer_of(full)
                s, per, lo = if_grade(rec, ans)
                g.write(json.dumps({"key": key, "pid": pid, "strict": s, "per": per, "loose": lo,
                                    "words": len(ans.split()) if ans is not None else None,
                                    "decode_ok": dec_ok, "has_close": "</think>" in r["text"]}) + "\n")
                n += 1
        print(f"{job}: {n} rows graded, decode mismatches {bad_dec}, file report {rep}, {time.time() - t0:.0f}s",
              flush=True)


if __name__ == "__main__":
    main()

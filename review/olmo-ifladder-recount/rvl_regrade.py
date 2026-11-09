"""Re-grade every stored sample of run olmo-ifladder with my own driver around the upstream checkers.

usage: rvl_regrade.py JOB [JOB ...]     -> out/regrade/<JOB>.jsonl.gz (one row per sample, file order)

Per row: pid, chunk, i, n_tok, finish, strict, loose, per (strict per-instruction), n_close (number of '</think>' in
the text), think_tok (ids up to and including the first '</think>', my piece table), dec_ok (text == my decode of the
stored ids with special tokens skipped), n_ids, ans_sha (sha256 of the whitespace-collapsed answer), ans_words
(whitespace words of the answer), ans_none. The grade uses the ORIGINAL upstream prompt and kwargs.
"""
import gzip
import json
import sys
import time

from rvl_core import OUT, Pieces, answer_of, iter_job, sha_text, unb64, upstream_record, wsnorm
from rvl_graders import if_grade

D = OUT / "regrade"
D.mkdir(exist_ok=True)
P = Pieces()


def main(jobs):
    for job in jobs:
        t0 = time.time()
        rep = {}
        n = 0
        with gzip.open(D / f"{job}.jsonl.gz.tmp", "wt") as fo:
            for r in iter_job(job, rep, with_ids=True):
                text = r["text"]
                ids = unb64(r["ids"])
                dec = P.text(ids)
                ans = answer_of(text)
                task, rec = upstream_record(r["pid"])
                st, per, lo = if_grade(task, rec, ans)
                k = P.first_close(ids)
                o = {"pid": r["pid"], "job": job, "model": r.get("model"), "chunk": r["chunk"], "i": r["i"],
                     "n_tok": r["n_tok"], "n_ids": len(ids), "finish": r["finish"], "strict": st, "loose": lo,
                     "per": per, "n_close": text.count("</think>"), "think_tok": k, "dec_ok": dec == text,
                     "ans_none": ans is None, "ans_sha": None if ans is None else sha_text(wsnorm(ans)),
                     "ans_words": None if ans is None else len(ans.split()),
                     "prompt_tokens": r.get("prompt_tokens"), "max_tokens": r.get("max_tokens")}
                fo.write(json.dumps(o) + "\n")
                n += 1
        (D / f"{job}.jsonl.gz.tmp").rename(D / f"{job}.jsonl.gz")
        with open(D / f"{job}.report.json", "w") as f:
            json.dump({"job": job, "rows": n, "read_report": rep, "secs": round(time.time() - t0, 1)}, f)
        print(job, n, rep, round(time.time() - t0, 1), "s", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])

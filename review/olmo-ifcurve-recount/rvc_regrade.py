"""Re-grade every stored sample used by run olmo-ifcurve with my own driver around the upstream checkers.

usage: rvc_regrade.py JOB [JOB ...]     -> out/regrade/<JOB>.jsonl.gz (one row per sample, file order)

Per row: pid, job, model, rev, chunk, i, n_tok, n_ids, finish, strict, loose, per (strict per-instruction), n_close
(number of '</think>' in the text), think_tok (response ids lying wholly before the FIRST '</think>', my piece
table), ans_tok (ids wholly after the LAST '</think>'), think_words / ans_words (whitespace words of the text before
the first '</think>' / of the stripped answer), dec_ok (text == my decode of the stored ids, special tokens skipped),
ans_none, ans_sha (sha256 of the whitespace-collapsed answer), ids_sha (sha256 of the response ids). The grade uses the
ORIGINAL upstream prompt and kwargs.
"""
import gzip
import json
import sys
import time

from rvc_core import OUT, Pieces, answer_of, iter_job, sha_int32, sha_text, thinking_of, unb64, upstream_record, wsnorm
from rvc_graders import if_grade

D = OUT / "regrade"
D.mkdir(exist_ok=True)
P = Pieces()
MK = b"</think>"


def spans(ids):
    """(think_tok, ans_tok) from byte offsets: ids wholly before the first marker / wholly after the last marker."""
    offs, pos = [], 0
    for i in ids:
        b = b"" if i in P.special else P.piece[i]
        offs.append((pos, pos + len(b)))
        pos += len(b)
    allb = P.bytes_of(ids)
    a = allb.find(MK)
    if a < 0:
        return None, None
    z = allb.rfind(MK) + len(MK)
    think = sum(1 for s, e in offs if e <= a)
    ans = sum(1 for s, e in offs if s >= z and e > s)
    return think, ans


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
                th = thinking_of(text)
                task, rec = upstream_record(r["pid"])
                st, per, lo = if_grade(task, rec, ans)
                tt, at = spans(ids)
                o = {"pid": r["pid"], "job": job, "model": r.get("model"), "rev": r.get("rev"), "chunk": r["chunk"],
                     "i": r["i"], "n_tok": r["n_tok"], "n_ids": len(ids), "finish": r["finish"], "strict": st,
                     "loose": lo, "per": per, "n_close": text.count("</think>"), "think_tok": tt, "ans_tok": at,
                     "think_words": None if th is None else len(th.split()),
                     "ans_words": None if ans is None else len(ans.split()), "dec_ok": dec == text,
                     "ans_none": ans is None, "ans_sha": None if ans is None else sha_text(wsnorm(ans)),
                     "ids_sha": sha_int32(ids), "prompt_tokens": r.get("prompt_tokens"),
                     "max_tokens": r.get("max_tokens")}
                fo.write(json.dumps(o) + "\n")
                n += 1
        (D / f"{job}.jsonl.gz.tmp").rename(D / f"{job}.jsonl.gz")
        with open(D / f"{job}.report.json", "w") as f:
            json.dump({"job": job, "rows": n, "read_report": rep, "secs": round(time.time() - t0, 1)}, f)
        print(job, n, rep, round(time.time() - t0, 1), "s", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])

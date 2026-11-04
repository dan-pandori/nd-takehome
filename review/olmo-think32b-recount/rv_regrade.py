"""Re-grade every stored sample text (reviewer code). Per sample: rl (open-instruct MathVerifier, real upstream
code, RL async path), main (same, main thread, diagnostic), my own final-stated-answer grade written from the
pre-registration text, and storage checks (ids length vs n_tok, last id). Usage: rv_regrade.py <samples.jsonl.gz> ...
Writes out/regrade_<job>.jsonl."""
import base64
import gzip
import hashlib
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import rv_upstream as U  # noqa: E402

LABEL = {}
for ln in open(os.path.join(ROOT, "olmo32", "problems.jsonl")):
    r = json.loads(ln)
    LABEL[r["pid"]] = str(r["answer"]).strip()
for ln in open(os.path.join(ROOT, "olmo32", "stage0_problems.jsonl")):
    r = json.loads(ln)
    LABEL.setdefault(r["pid"], str(r["answer"]).strip())


def _match_brace(s, i):
    """s[i] == '{' -> index of the matching '}', or -1."""
    depth = 0
    for j in range(i, len(s)):
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
            if depth == 0:
                return j
    return -1


def _as_int(span):
    """An integer, or '<anything> = <integer>'; LaTeX decoration removed. Else None."""
    s = span
    s = re.sub(r"\\(text|textbf|mathrm|mathbf|displaystyle|boldsymbol|operatorname)\b", "", s)
    for x in ("\\left", "\\right", "\\,", "\\;", "\\!", "\\ ", "\\%", "%", "$", "{", "}", "^\\circ", "\\circ"):
        s = s.replace(x, "")
    s = re.sub(r"\s+", "", s)
    s = re.sub(r"(?<=\d),(?=\d\d\d(\D|$))", "", s)
    s = s.rstrip(".")
    if re.fullmatch(r"-?\d+", s):
        return int(s)
    if "=" in s:
        t = s.rsplit("=", 1)[1]
        if re.fullmatch(r"-?\d+", t):
            return int(t)
    return None


def my_final(text):
    """(think_end, source, value) under the pre-registered final-stated-answer rule."""
    j = text.rfind("</think>")
    if j < 0:
        return False, None, None
    tail = text[j + len("</think>"):]
    k = tail.rfind("\\boxed{")
    if k >= 0:
        e = _match_brace(tail, k + len("\\boxed"))
        inner = tail[k + len("\\boxed{"): e] if e >= 0 else tail[k + len("\\boxed{"):]
        return True, "boxed", _as_int(inner)
    lines = [ln for ln in tail.split("\n") if "answer" in ln.lower()]
    if lines:
        low = lines[-1].lower()
        after = lines[-1][low.rfind("answer") + len("answer"):]
        after = re.sub(r"(?<=\d),(?=\d\d\d(\D|$))", "", after)
        ints = re.findall(r"-?\d+", after)
        return True, "line", (int(ints[-1]) if ints else None)
    return True, None, None


def main():
    for path in sys.argv[1:]:
        job = os.path.basename(path).replace(".jsonl.gz", "")
        out = os.path.join(HERE, "out", f"regrade_{job}.jsonl")
        n = 0
        with gzip.open(path, "rt") as f, open(out, "w") as g:
            for ln in f:
                r = json.loads(ln)
                lab = LABEL[r["pid"]]
                ids = np.frombuffer(base64.b64decode(r["ids"]), dtype=np.int32)
                te, src, val = my_final(r["text"])
                row = {k: r[k] for k in ("pid", "model", "rev", "job", "chunk", "i", "n_tok", "finish")}
                row.update({
                    "n_ids": int(len(ids)), "last_id": int(ids[-1]) if len(ids) else None,
                    "eos_inside": int((ids[:-1] == 100257).sum()) if len(ids) > 1 else 0,
                    "text_sha": hashlib.sha256(r["text"].encode()).hexdigest()[:16],
                    "rl": U.rl_grade(r["text"], lab), "main": U.main_grade(r["text"], lab),
                    "final": (val is not None and str(val) == str(int(lab))), "think_end": te,
                    "final_src": src, "final_val": val, "label": lab,
                })
                g.write(json.dumps(row) + "\n")
                n += 1
        print(job, n, flush=True)


if __name__ == "__main__":
    main()

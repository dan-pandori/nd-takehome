#!/usr/bin/env python3
"""Grade every response of a samples file as if it had been cut at 32,768 tokens (run olmo-iffu, test 1).

The model's distribution over the first 32,768 response tokens does not depend on the budget, so the first 32,768 of
a 65k-budget draw's stored ids are a draw at olmo-ifomega's cap. Decodes ids[:CUT] (skip_special_tokens=True, as the
sampler decodes) and grades with olmo_ifomega/grade.grade_one. Responses of <= CUT tokens are graded on their stored
text (identical). Usage: grade_trunc.py <samples.jsonl.gz> <problems.jsonl> <out.jsonl> [--tok /workspace/models/tok]
"""
import base64
import gzip
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "olmo_ifomega"))
import grade  # noqa: E402

CUT = 32768


def main():
    samples, problems, out = sys.argv[1:4]
    tokdir = sys.argv[sys.argv.index("--tok") + 1] if "--tok" in sys.argv else "/workspace/models/tok"
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(tokdir)
    probs = {r["pid"]: r for r in map(json.loads, open(problems))}
    n = 0
    with gzip.open(samples, "rt") as f, open(out, "w") as g:
        for ln in f:
            try:
                r = json.loads(ln)
            except json.JSONDecodeError:
                break
            p = probs[r["pid"]]
            if r["n_tok"] > CUT:
                ids = np.frombuffer(base64.b64decode(r["ids"]), dtype=np.int32)[:CUT].tolist()
                text, fin = tok.decode(ids, skip_special_tokens=True), "length"
            else:
                text, fin = r["text"], r["finish"]
            row = {k: r[k] for k in ("pid", "model", "job", "chunk", "i", "n_tok", "finish")}
            row.update({"cut": CUT, "finish_cut": fin, "n_tok_cut": min(r["n_tok"], CUT)})
            row.update(grade.grade_one(p["task"], text, p))
            g.write(json.dumps(row) + "\n")
            n += 1
    print(f"graded {n} at {CUT} -> {out}")


if __name__ == "__main__":
    sys.exit(main())

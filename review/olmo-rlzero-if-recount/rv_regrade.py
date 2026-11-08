#!/usr/bin/env python3
"""Re-grade every stored sample text with my graders and check the stored token ids.

Per row: strict / loose / per (rv_graders), random_dep, think_end ('</think>' in text), ans_tag, ids checks
(decode(ids, skip_special_tokens=True) == text with the tokenizer the job used; n_tok == len(ids); finish 'length' iff
len(ids) == cap; ends in EOS 100257), counts of the RL-Zero-IF tag ids, and my own first-turn grade `t1` (strict on
the extraction of decode(ids before the first <|endoftext|> / <|im_start|> / <|im_end|>)).
Usage: rv_regrade.py JOB [JOB ...]   -> out/regrade/<JOB>.jsonl (no text)"""
import json
import os
import sys
import time

from tokenizers import Tokenizer

from rv_core import (ANS_CLOSE, ANS_OPEN, BIG, CAP, OUT, THINK_CLOSE, THINK_OPEN, TURN_IDS, ids_of, iter_gz_lines,
                     iter_rows, load_problems, remove_thinking_section, SAMPLES)
from rv_graders import grade, if_check, random_dep

TOK_RL = Tokenizer.from_file(os.path.join(BIG, "hf", "allenai_Olmo-3-7B-RL-Zero-IF@main", "tokenizer.json"))
TOK_BASE = Tokenizer.from_file(os.path.join(BIG, "hf", "allenai_Olmo-3-1025-7B@main", "tokenizer.json"))
IF_TASKS = ("ifbench", "ifeval")


def main():
    P = load_problems()
    P0 = load_problems(stage0=True)
    os.makedirs(os.path.join(OUT, "regrade"), exist_ok=True)
    for job in sys.argv[1:]:
        t0 = time.time()
        tok = TOK_BASE if job.startswith("D_base_btok") else TOK_RL
        out = os.path.join(OUT, "regrade", f"{job}.jsonl")
        n = 0
        with open(out + ".tmp", "w") as g:
            for r in iter_rows(job):
                pid = r["pid"]
                prob = P.get(pid) or P0.get(pid)
                ids = ids_of(r) if r.get("ids") is not None else None
                text = r["text"]
                row = {k: r.get(k) for k in ("pid", "model", "rev", "job", "chunk", "i", "n_tok", "finish",
                                             "stop_reason")}
                row["task"] = prob["task"]
                if ids is None:  # a row the executor redacted before publishing (ids dropped)
                    row["redacted"] = r.get("redacted", True)
                    ids = []
                    row["dec_eq"] = None
                else:
                    row["dec_eq"] = tok.decode(ids, skip_special_tokens=True) == text
                row["n_ids"] = len(ids)
                row["eos_end"] = bool(ids) and ids[-1] == 100257
                row["len_cap"] = len(ids) >= CAP
                row["n_think_open"] = ids.count(THINK_OPEN)
                row["n_think_close"] = ids.count(THINK_CLOSE)
                row["n_ans_open"] = ids.count(ANS_OPEN)
                row["n_ans_close"] = ids.count(ANS_CLOSE)
                row["n_turn"] = sum(x in TURN_IDS[1:] for x in ids)
                row["think_end"] = "</think>" in text
                row["ans_tag"] = "<answer>" in text
                if prob["task"] in IF_TASKS:
                    row.update(grade(prob["task"], prob, text))
                    row["random_dep"] = bool(random_dep(prob))
                    k = next((j for j, x in enumerate(ids) if x in TURN_IDS), None)
                    if k is not None and k < len(ids) - 1:
                        a1 = remove_thinking_section(tok.decode(ids[:k], skip_special_tokens=True))
                        row["t1"] = if_check(prob["task"], prob, a1)[0] if a1 else False
                        row["cont"] = bool(tok.decode(ids[k:], skip_special_tokens=True).strip())
                    else:
                        row["t1"], row["cont"] = row["strict"], False
                g.write(json.dumps(row) + "\n")
                n += 1
        os.replace(out + ".tmp", out)
        dmg = iter_gz_lines.damage.get(os.path.join(SAMPLES, f"{job}.jsonl.gz"))
        print(f"{job}: {n} rows in {time.time() - t0:.0f}s damage={dmg}", flush=True)


if __name__ == "__main__":
    sys.exit(main())

"""Re-grade every stored sample of run olmo-ifomega with the reviewer graders (rv_graders.py), plus storage checks.

Usage: ~/review/oif_venv/bin/python rv_regrade.py JOB [JOB ...]   -> out/regrade/<JOB>.jsonl (one row per sample, no text)
Row: pid task model rev job chunk i n_tok finish ids_n ids_last think_end + grades:
  IF   : strict per loose rlview ans_words ans_sha
  OMEGA: omega omega_ans omega_fmt rl own own_ans
Storage damage (gzip members, truncation) -> out/regrade/<JOB>.damage.json"""
import base64
import hashlib
import json
import os
import sys
import time

import numpy as np

import rv_core as C
import rv_graders as G

IF_TASKS = ("ifbench", "ifeval")
OM_TASKS = ("omega_in", "omega_out")


def main(jobs):
    P = C.load_problems()
    P.update(C.load_problems(stage0=True))
    od = os.path.join(C.OUT, "regrade")
    os.makedirs(od, exist_ok=True)
    for job in jobs:
        t0 = time.time()
        rows = 0
        tmp = os.path.join(od, f"{job}.jsonl.tmp")
        with open(tmp, "w") as g:
            for r in C.iter_rows(job):
                p = P[r["pid"]]
                ids = np.frombuffer(base64.b64decode(r["ids"]), dtype=np.int32)
                text = r["text"]
                ans = C.answer_of(text)
                o = {k: r[k] for k in ("pid", "model", "rev", "job", "chunk", "i", "n_tok", "finish")}
                o.update(task=p["task"], ids_n=int(len(ids)), ids_last=int(ids[-1]) if len(ids) else None,
                         think_end=ans is not None, think_n=text.count("</think>"), text_len=len(text))
                if p["task"] in IF_TASKS:
                    if ans is None or not ans:
                        n = len(p["instruction_id_list"])
                        o.update(strict=False, per=[False] * n, loose=False)
                    else:
                        o["strict"], o["per"] = G.if_check(p["task"], p, ans)
                        o["loose"] = G.if_check(p["task"], p, ans, loose=True)[0]
                    rv = G._gtu.remove_thinking_section(text)
                    o["rlview"] = G.if_check(p["task"], p, rv)[0] if rv else False
                    o["ans_words"] = len(ans.split()) if ans else 0
                    o["ans_sha"] = hashlib.sha1(ans.encode()).hexdigest()[:12] if ans is not None else None
                elif p["task"] in OM_TASKS:
                    lab = p["answer"]
                    o["omega"], o["omega_ans"], o["omega_fmt"] = G.omega_grade(ans, lab)
                    o["omega_ans"] = o["omega_ans"][:120]
                    o["rl"] = G.rl_grade(text, lab)
                    o["own"], own_ans = G.own_grade(ans, lab)
                    o["own_ans"] = own_ans[:120] if own_ans is not None else None
                g.write(json.dumps(o) + "\n")
                rows += 1
        os.replace(tmp, os.path.join(od, f"{job}.jsonl"))
        dmg = C.iter_gz_lines.damage.get(os.path.join(C.SAMPLES, f"{job}.jsonl.gz"), [])
        json.dump({"job": job, "rows": rows, "damage": dmg}, open(os.path.join(od, f"{job}.damage.json"), "w"))
        print(f"{job}: {rows} rows {time.time() - t0:.0f}s {dmg}", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])

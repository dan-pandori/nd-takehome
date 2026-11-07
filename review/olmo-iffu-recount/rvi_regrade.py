"""Re-grade every stored sample of run olmo-iffu with my own driver (rvi_graders) and check text vs ids.

Per row (no text): job, pid, model, rev, chunk, i, n_tok, finish, max_tokens, prompt_tokens; ids length, last id,
text == decode(ids, skip_special_tokens) ; think_end, answer words (whitespace split, the hint's diagnostic);
IF: strict, per-constraint, loose; OMEGA: omega (OLMES exact_match_flex on the answer), its extracted answer,
rl (MathVerifier, worker thread), rl_main (main thread), and the same three on the response truncated to its first
32,768 tokens (decoded from the stored ids).
Problems: IF records come from the upstream datasets (my fetch), keyed by the pid's number; OMEGA labels are my own
(rvi_labels.py, out/labels.json).
Usage: rvi_regrade.py [job ...]   -> out/regrade/<job>.jsonl.gz
"""
import gzip
import json
import sys
import time

from tokenizers import Tokenizer

import rvi_core as C
import rvi_graders as G

TOK = Tokenizer.from_file(str(C.SCR / "tok" / "allenai_Olmo-3-32B-Think-DPO" / "tokenizer.json"))
TOK31 = Tokenizer.from_file(str(C.SCR / "tok" / "allenai_Olmo-3.1-32B-Think" / "tokenizer.json"))
CUT = 32768


def decode(ids, tok):
    return tok.decode(ids, skip_special_tokens=True)


def main():
    jobs = sys.argv[1:] or C.JOBS
    ifb, ife = C.upstream_ifbench(), C.upstream_ifeval()
    labels = json.load(open(C.OUT / "labels.json"))["label"]
    (C.OUT / "regrade").mkdir(exist_ok=True)
    for job in jobs:
        t0 = time.time()
        rep = {}
        n = 0
        with gzip.open(C.OUT / "regrade" / f"{job}.jsonl.gz", "wt") as g:
            for r in C.iter_rows(job, with_ids=True, report=rep):
                ids = C.ids_of(r)
                tok = TOK if r["model"] == "dpo" else TOK31
                text = r["text"]
                o = {k: r[k] for k in ("job", "pid", "model", "rev", "chunk", "i", "n_tok", "finish", "max_tokens",
                                       "prompt_tokens", "stop_reason")}
                o["ids_len"] = len(ids)
                o["last_id"] = ids[-1] if ids else None
                o["text_eq_decode"] = decode(ids, tok) == text
                ans = C.answer_of(text)
                o["think_end"] = ans is not None
                o["answer_words"] = len(ans.split()) if ans is not None else None
                pid = r["pid"]
                if pid.startswith(("ifbench_", "ifeval_")):
                    task = pid.split("_")[0]
                    rec = (ifb if task == "ifbench" else ife)[pid.split("_")[1]]
                    o["strict"], o["per"], o["loose"] = G.if_grade(task, rec, ans)
                else:
                    lab = labels[pid]
                    o["omega"], o["omega_ans"] = G.omega_grade(text, lab)
                    o["omega_ans"] = o["omega_ans"][:120]
                    o["rl"] = G.rl_grade(text, lab)
                    o["rl_main"] = G.rl_grade_main(text, lab)
                    tt = decode(ids[:CUT], tok) if len(ids) > CUT else text
                    o["t32_think_end"] = C.answer_of(tt) is not None
                    o["t32_omega"], _ = G.omega_grade(tt, lab)
                    o["t32_rl"] = G.rl_grade(tt, lab)
                    o["t32_rl_main"] = G.rl_grade_main(tt, lab)
                    o["omega_stored_label"] = G.omega_grade(text, "17")[0] if pid.endswith("_055") else None
                g.write(json.dumps(o) + "\n")
                n += 1
        print(f"{job}: {n} rows, damage {rep}, {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()

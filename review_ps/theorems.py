"""Theorem-level labels with the reviewer's own G4ip + truth tables.
usage: python3 theorems.py <name> <file> [proof_field]"""
import gzip
import json
import sys
import time
from nd import parse_prompt, Proof, subformulas
from ipc import intuitionistic, classically_valid, satisfiable


def opener(fn):
    return gzip.open(fn, "rt") if fn.endswith(".gz") else open(fn)


def dneg(prem, concl):
    S = set()
    for f in prem + [concl]:
        subformulas(f, S)
    syn = sem = False
    for f in S:
        if isinstance(f, tuple):
            if f[0] == "~" and isinstance(f[1], tuple) and f[1][0] == "~":
                syn = sem = True
            if f[0] == ">" and f[2] == "F" and isinstance(f[1], tuple) and (
                    f[1][0] == "~" or (f[1][0] == ">" and f[1][2] == "F")):
                sem = True
            if f[0] == "~" and isinstance(f[1], tuple) and f[1][0] == ">" and f[1][2] == "F":
                sem = True
    return syn, sem


def main():
    name, fn = sys.argv[1], sys.argv[2]
    field = sys.argv[3] if len(sys.argv) > 3 else None
    out = gzip.open(f"out/thm_{name}.jsonl.gz", "wt")
    t0 = time.time()
    bad = 0
    for i, line in enumerate(opener(fn)):
        r = json.loads(line)
        prem, concl = parse_prompt(r["prompt"])
        cv = classically_valid(prem, concl)
        iv = intuitionistic(prem, concl)
        syn, sem = dneg(prem, concl)
        inc = not satisfiable(prem) if prem else False
        rec = {"i": i, "name": r.get("name"), "cv": cv, "iv": iv, "co": cv and not iv, "dneg_syn": syn, "dneg_sem": sem,
               "inc": inc, "sc_syn": cv and not iv and not syn, "sc_sem": cv and not iv and not sem}
        if field and r.get(field):
            P = Proof(prem, concl, r[field])
            has_dn = any(P.L[k]["rule"] == "DN" for k in P.order)
            rec["proof_dn"] = has_dn
            if not has_dn and not iv:
                bad += 1
                rec["CONTRA"] = True
            if not cv:
                bad += 1
                rec["CONTRA_CV"] = True
        out.write(json.dumps(rec) + "\n")
    out.close()
    print(name, "rows", i + 1, "contradictions", bad, "secs %.0f" % (time.time() - t0), file=sys.stderr)


if __name__ == "__main__":
    main()

"""Classify every record of a set with the reviewer's classifier; write per-record labels (gz jsonl).
usage: python3 run_sets.py <set_name> <file> <proof_field> [--written]"""
import gzip
import json
import sys
import time
from nd import Proof, parse_prompt, ParseError
from cls import classify

STRATS = ["direct", "and_intro", "cond_proof", "or_intro", "cases", "disj_syll", "neg_intro", "mod_tollens",
          "ex_falso", "contradiction", "dne", "lem", "lemma_reuse"]


def opener(fn):
    return gzip.open(fn, "rt") if fn.endswith(".gz") else open(fn)


def main():
    name, fn, field = sys.argv[1], sys.argv[2], sys.argv[3]
    keep_ok = "--lean_ok" in sys.argv
    out = gzip.open(f"out/labels_{name}.jsonl.gz", "wt")
    t0 = time.time()
    n = 0
    for i, line in enumerate(opener(fn)):
        r = json.loads(line)
        proof = r.get(field)
        rec = {"i": i, "name": r.get("name")}
        if keep_ok and not r.get("lean_ok"):
            rec["skip"] = "not lean_ok"
            out.write(json.dumps(rec) + "\n")
            continue
        if not proof:
            rec["skip"] = "no proof"
            out.write(json.dumps(rec) + "\n")
            continue
        try:
            prem, concl = parse_prompt(r["prompt"])
            P = Proof(prem, concl, proof)
            ok, why = P.check()
            o = classify(prem, concl, proof, pruned=True, P=P)
            w = classify(prem, concl, proof, pruned=False, P=P)
        except (ParseError, ValueError, KeyError, IndexError, AssertionError) as ex:
            rec["skip"] = "parse " + repr(ex)[:80]
            out.write(json.dumps(rec) + "\n")
            continue
        rec.update({"ndok": ok, "why": why, "uses": sorted(o["uses"]), "work": sorted(o["work"]),
                    "sub": sorted("%s.%s" % k for k in o["sub"]), "primary": o["primary"], "curried": o["curried"],
                    "boxfree": o["boxfree"], "v0": sorted(o["v0"]), "sigma": o["sigma"],
                    "sigma_strict": o["sigma_strict"], "sigma_plus": o["sigma_plus"],
                    "n_lines": o["n_lines"], "n_kept": o["n_kept"], "depth": o["depth"],
                    "w_uses": sorted(w["uses"]), "w_sigma": w["sigma"], "w_sub": sorted("%s.%s" % k for k in w["sub"])})
        out.write(json.dumps(rec) + "\n")
        n += 1
    out.close()
    print(name, "records", i + 1, "classified", n, "secs %.0f" % (time.time() - t0), file=sys.stderr)


if __name__ == "__main__":
    main()

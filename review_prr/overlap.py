"""Reviewer's own exposure check: which evaluation theorems have a substitution instance (or a renaming-class twin)
among a training pool.  Usage: python3 review_prr/overlap.py <train.jsonl[.gz]> [more train files] > out
Run from the workspace root.  Directions reported:
  inst  : some training sequent X = sigma(E) for the evaluation sequent E (X is an instance of E's schema)
  gen   : E = sigma(X) for some training X (E is an instance of a training schema)
  ren   : X and E are the same sequent up to an atom bijection (premise order ignored)
  ren_o : same, but premise order respected (the project's historical `canon_key`-style notion)
"""
import collections
import gzip
import json
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import fml  # noqa: E402

EVAL = {
    "tb72_dev58": ["data/gt/tb72_textbook_dev.jsonl"],
    "tb72_train14": ["data/gt/tb72_textbook_train.jsonl"],
    "c_v0_87": ["data/gt/candidate_v0.jsonl"],
    "c_v1_72": ["data/gt/candidate_v1.jsonl"],
    "c_b3_14": ["data/gt/batch3.jsonl"],
    "c_hand14": ["data/gt/hand_proved_14.jsonl"],
}


def read(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as fh:
        for line in fh:
            if line.strip():
                yield json.loads(line)


def seq_of(rec):
    if rec.get("prompt"):
        return fml.parse_prompt(rec["prompt"])
    raise KeyError("no prompt")


def main(train_files):
    train = []
    bad = 0
    for p in train_files:
        for r in read(p):
            try:
                train.append((r.get("name"), seq_of(r)))
            except Exception:
                bad += 1
    print(f"training sequents: {len(train)} from {train_files} (unparsed {bad})")
    # index training sequents by (n_prem, conclusion top constructor) for speed
    idx = collections.defaultdict(list)
    for nm, (pp, c) in train:
        idx[len(pp)].append((nm, (pp, c)))
    ren_keys = collections.defaultdict(list)
    for nm, (pp, c) in train:
        ren_keys[fml.rename_canon(pp, c)].append(nm)
    out = {}
    for ename, files in EVAL.items():
        recs = [r for f in files for r in read(f)]
        hits = {"inst": [], "gen": [], "ren": [], "ren_o": []}
        for r in recs:
            E = seq_of(r)
            n = len(E[0])
            cands = idx.get(n, [])
            inst = [nm for nm, X in cands if fml.match_seq(E, X) is not None]
            gen = [nm for nm, X in cands if fml.match_seq(X, E) is not None]
            ren = ren_keys.get(fml.rename_canon(*E), [])
            ren_o = [nm for nm, X in cands
                     if (s := fml.match_seq(E, X, ordered=True)) is not None and fml.is_renaming(s)]
            for key, lst in (("inst", inst), ("gen", gen), ("ren", ren), ("ren_o", ren_o)):
                if lst:
                    # textbook72 is scored by id only (hygiene); Charles's sets are public in data/gt
                    hits[key].append({"name": r["name"],
                                      "seq": None if ename.startswith("tb72") else fml.show_seq(*E),
                                      "n": len(lst), "example": lst[0]})
        out[ename] = {"n": len(recs), **{k: v for k, v in hits.items()}}
        print(f"{ename:<13} n={len(recs):>3}  inst {len(hits['inst']):>3}  gen {len(hits['gen']):>3}  "
              f"ren {len(hits['ren']):>3}  ren_o {len(hits['ren_o']):>3}")
    return out


if __name__ == "__main__":
    res = main(sys.argv[1:])
    json.dump(res, open("review_prr/out/overlap_" + sys.argv[1].rsplit("/", 1)[-1].split(".")[0] + ".json", "w"),
              indent=1, ensure_ascii=False)

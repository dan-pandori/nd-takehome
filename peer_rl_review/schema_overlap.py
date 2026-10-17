"""Design exposure on our side: which of our T1-ladder RL targets are substitution instances of a textbook72 or
Charles173 theorem (the mirror of the dev58 caveat on Leon's RL generator).

A target T is an instance of an eval theorem E if one substitution sigma (atoms of E -> formulas) maps E's goal to T's
goal and E's premises onto T's premises as a multiset (same premise count, any order). "Renaming class" = sigma maps
atoms to distinct atoms (the key the project seals eval sets with). Pure Python, CPU only.

Usage: python3 peer_rl_review/schema_overlap.py > peer_rl_review/out/schema_overlap.txt
"""
import collections
import itertools
import json

BIN = {"&", "v", ">"}


def parse_formula(toks, i):
    t = toks[i]
    if t != "(":
        return t, i + 1  # atom or F
    if toks[i + 1] == "~":
        sub, j = parse_formula(toks, i + 2)
        assert toks[j] == ")", toks
        return ("~", sub), j + 1
    left, j = parse_formula(toks, i + 1)
    op = toks[j]
    assert op in BIN, (op, toks)
    right, k = parse_formula(toks, j + 1)
    assert toks[k] == ")", toks
    return (op, left, right), k + 1


def parse_prompt(prompt):
    toks = prompt.split()
    assert toks[0] == "THM" and toks[-1] == "PRF", prompt
    s = toks.index("SEQ")
    prem_toks, goal_toks = toks[1:s], toks[s + 1:-1]
    prems, i = [], 0
    while i < len(prem_toks):
        f, i = parse_formula(prem_toks, i)
        prems.append(f)
        if i < len(prem_toks):
            assert prem_toks[i] == ",", prompt
            i += 1
    goal, j = parse_formula(goal_toks, 0)
    assert j == len(goal_toks), prompt
    return prems, goal


def is_atom(f):
    return isinstance(f, str) and f != "F"


def match(pat, tgt, sigma):
    """Extend sigma so that sigma(pat) == tgt; return the new sigma or None."""
    if is_atom(pat):
        if pat in sigma:
            return sigma if sigma[pat] == tgt else None
        s = dict(sigma)
        s[pat] = tgt
        return s
    if isinstance(pat, str):  # F
        return sigma if pat == tgt else None
    if not isinstance(tgt, tuple) or tgt[0] != pat[0] or len(tgt) != len(pat):
        return None
    for a, b in zip(pat[1:], tgt[1:]):
        sigma = match(a, b, sigma)
        if sigma is None:
            return None
    return sigma


def instance(E, T):
    """Return sigma if T is a substitution instance of E (premises as a multiset), else None."""
    (ep, eg), (tp, tg) = E, T
    if len(ep) != len(tp):
        return None
    s0 = match(eg, tg, {})
    if s0 is None:
        return None
    for perm in itertools.permutations(range(len(tp))):
        s = s0
        for a, b in zip(ep, [tp[p] for p in perm]):
            s = match(a, b, s)
            if s is None:
                break
        if s is not None:
            return s
    return None


def renaming(sigma):
    vals = list(sigma.values())
    return all(is_atom(v) for v in vals) and len(set(vals)) == len(vals)


def load(path):
    return [json.loads(l) for l in open(path)]


def main():
    evals = {}
    for name, files in [("textbook72", ["data/gt/tb72_textbook_dev.jsonl", "data/gt/tb72_textbook_train.jsonl"]),
                        ("charles173", ["data/gt/candidate_v0.jsonl", "data/gt/candidate_v1.jsonl",
                                        "data/gt/batch3.jsonl"])]:
        evals[name] = [(r["name"], parse_prompt(r["prompt"])) for f in files for r in load(f)]
    dev = {json.loads(l)["name"] for l in open("data/gt/tb72_textbook_dev.jsonl")}
    tgts = load("data/ladder/rl_targets.jsonl")
    parsed = [parse_prompt(r["prompt"]) for r in tgts]
    print(__doc__.split("\n")[0])
    print(f"targets: data/ladder/rl_targets.jsonl ({len(tgts)}; source counts "
          f"{dict(collections.Counter(r['source'] for r in tgts))})\n")
    for ename, E in evals.items():
        hit_t = collections.defaultdict(set)   # target index -> eval names
        hit_e = collections.defaultdict(set)   # eval name -> target indices
        ren = 0
        for ti, T in enumerate(parsed):
            for en, ep in E:
                s = instance(ep, T)
                if s is not None:
                    hit_t[ti].add(en)
                    hit_e[en].add(ti)
                    ren += renaming(s)
        by_src = collections.Counter(tgts[ti]["source"] for ti in hit_t)
        by_schema = collections.Counter(tgts[ti].get("schema") for ti in hit_t)
        print(f"== {ename} ({len(E)} theorems)")
        print(f"  targets that are an instance of >= 1 {ename} theorem: {len(hit_t)} (by source {dict(by_src)})")
        print(f"  of which pure renamings (same renaming class): {ren} pair(s)")
        print(f"  {ename} theorems with >= 1 instance among the targets: {len(hit_e)}"
              + (f" (dev58: {len(set(hit_e) & dev)}, train14: {len(set(hit_e) - dev)})" if ename == "textbook72" else ""))
        print(f"  targets per schema: {dict(by_schema.most_common())}")
        sizes = sorted((len(v) for v in hit_e.values()), reverse=True)
        print(f"  instances per covered theorem (desc): {sizes}\n")
        if ename == "textbook72":
            json.dump(sorted(hit_e), open("peer_rl_review/out/tb72_with_target_instances.json", "w"), indent=0)


if __name__ == "__main__":
    main()

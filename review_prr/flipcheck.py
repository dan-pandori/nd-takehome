"""Are the single-flip controls that Lean still accepts benign no-ops?  For each accepted flip, report the flipped
token's context: an Or.inl/Or.inr whose `have` type is `( X ∨ X )`, or a .1/.2 on a `( X ∧ X )` hypothesis, is benign.
python3 review_prr/flipcheck.py > review_prr/out/flipcheck.txt
"""
import random
import re
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import leanrc  # noqa: E402
import reads  # noqa: E402

rng = random.Random(7)


def split_top(s):
    """split an `( A op B )` string into A, op, B at depth 1"""
    toks = s.split()
    assert toks[0] == "(" and toks[-1] == ")"
    d = 0
    for i, t in enumerate(toks[1:-1], 1):
        if t == "(":
            d += 1
        elif t == ")":
            d -= 1
        elif d == 0 and t in ("∧", "∨", "→"):
            return " ".join(toks[1:i]), t, " ".join(toks[i + 1:-1])
    return None


def main():
    texts = []
    for lab in ["gt_best12_r8_plain (trajectory seeds)", "gt_best12_r8_guided (trajectory seeds)", "cd_r16_guided"]:
        for s, (p, _) in reads.arms()[lab].items():
            for r in reads.jl(p):
                for t in (r.get("accepted") or {}):
                    texts.append((r["prompt"], t))
    rng.shuffle(texts)
    items, meta = [], []
    for pr, t in texts:
        spots = [(m.start(), m.group(0)) for m in re.finditer(r"Or\.inl|Or\.inr", t)]
        if not spots:
            continue
        pos, tok = rng.choice(spots)
        rep = "Or.inr" if tok == "Or.inl" else "Or.inl"
        items.append((pr, t[:pos] + rep + t[pos + len(tok):]))
        # the have whose term this is: last 'have nK : <type> :=' before pos
        hs = list(re.finditer(r"have n\d+ : (.*?) := ", t[:pos]))
        ty = hs[-1].group(1) if hs else None
        meta.append((ty, t[pos:pos + 40]))
        if len(items) >= 400:
            break
    res = leanrc.check(items)
    acc = [(m, it) for (ok, _), m, it in zip(res, meta, items) if ok]
    print(f"Or.inl<->Or.inr flips: {len(items)} checked, {len(acc)} still accepted")
    benign = 0
    for (ty, ctx), it in acc:
        sp = split_top(ty) if ty and ty.startswith("(") else None
        sym = bool(sp and sp[1] == "∨" and sp[0] == sp[2])
        benign += sym
        print(f"  {'SYMMETRIC' if sym else 'CHECK    '} have-type {ty} | {ctx}")
    print(f"accepted flips whose `have` type is ( X ∨ X ): {benign} of {len(acc)}")


if __name__ == "__main__":
    main()

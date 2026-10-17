"""Accepted .1<->.2 flips: is the projected hypothesis of type ( X ∧ X )?  python3 review_prr/flipcheck2.py"""
import random, re, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import leanrc, reads
from flipcheck import split_top
rng = random.Random(11)
texts = []
for lab in ["gt_best12_r8_plain (trajectory seeds)", "gt_best12_r8_guided (trajectory seeds)", "cd_r16_guided"]:
    for s, (p, _) in reads.arms()[lab].items():
        for r in reads.jl(p):
            for t in (r.get("accepted") or {}):
                texts.append((r["prompt"], t))
rng.shuffle(texts)
items, meta = [], []
for pr, t in texts:
    spots = [m for m in re.finditer(r"(n\d+)\.([12])(?=\s)", t)]
    if not spots:
        continue
    m = rng.choice(spots)
    name, side = m.group(1), m.group(2)
    items.append((pr, t[:m.start(2)] + ("2" if side == "1" else "1") + t[m.end(2):]))
    # names are re-bound in sibling boxes: take the nearest binding before the use
    decls = list(re.finditer(r"(?:have " + name + r" : (.*?) := )|(?:\( " + name + r" : (.*?) \) =>)", t[:m.start()]))
    ty = (decls[-1].group(1) or decls[-1].group(2)) if decls else None
    meta.append(ty)
    if len(items) >= 400:
        break
res = leanrc.check(items)
acc = [ty for (ok, _), ty in zip(res, meta) if ok]
sym = 0
for ty in acc:
    sp = split_top(ty) if ty and ty.startswith("(") else None
    s_ = bool(sp and sp[1] == "∧" and sp[0] == sp[2])
    sym += s_
    print(("SYMMETRIC " if s_ else "CHECK     ") + str(ty))
print(f".1<->.2 flips: {len(items)} checked, {len(acc)} still accepted, of which ( X ∧ X ): {sym}")

"""Reviewer's Lean re-check of counted proofs behind peer-rl-review's numbers, with negative controls first.

Run from the workspace root:  python3 review_prr/recheck.py > review_prr/out/recheck.txt
Literal texts: guided-tts / capability-defs rows (`accepted` dicts) and best-state gate dumps (`lean_text`).
ND-only reads (rl-continue r16 x1, grpo-best r8): own ND->Lean rendering (leanrc.nd_to_lean), validated on the dumps.
"""
import collections
import random
import re
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import leanrc  # noqa: E402
import reads  # noqa: E402
import fml  # noqa: E402

rng = random.Random(20261017)
TB = set(reads.TB72)
C173 = set(reads.C_V0 + reads.C_V1 + reads.C_B3)
def sample_cover(per_thm, fill, cap_extra):
    """per_thm: {name: [texts]} -> one text per theorem, then random extra tb72 texts until >= cap_extra items"""
    out = [(nm, rng.choice(texts)) for nm, texts in sorted(per_thm.items())]
    seen = set(out)
    pool = [(nm, t) for nm, texts in sorted(per_thm.items()) if nm in TB for t in texts if (nm, t) not in seen]
    rng.shuffle(pool)
    while fill and len(out) < cap_extra and pool:
        out.append(pool.pop())
    return out


def report(label, items, res):
    n = len(res)
    acc = sum(ok for ok, _ in res)
    why = collections.Counter(r for ok, r in res if not ok)
    print(f"{label:<58} checked {n:>5}  accepted {acc:>5}  rejected {n - acc:>4}  {dict(why)}", flush=True)
    return acc, n


def flip_once(text):
    """flip one Or.inl<->Or.inr or .1<->.2 occurrence (random position); None if nothing to flip"""
    spots = [(m.start(), m.group(0)) for m in re.finditer(r"Or\.inl|Or\.inr|\.1(?=\s)|\.2(?=\s)", text)]
    if not spots:
        return None
    pos, tok = rng.choice(spots)
    rep = {"Or.inl": "Or.inr", "Or.inr": "Or.inl", ".1": ".2", ".2": ".1"}[tok]
    return text[:pos] + rep + text[pos + len(tok):]


def main():
    # ---------- load literal texts ----------
    lit = {}  # arm-seed label -> {theorem: [texts]}
    prompts = {}
    for lab in ["gt_best12_r8_plain (trajectory seeds)", "gt_best12_r8_guided (trajectory seeds)", "cd_r16_guided"]:
        for s, (p, _) in reads.arms()[lab].items():
            d = {}
            for r in reads.jl(p):
                prompts[r["name"]] = r["prompt"]
                if r["n_ok"] > 0:
                    assert r["accepted"], (p, r["name"])
                    assert sum(r["accepted"].values()) == r["n_ok"], (p, r["name"], "accepted counts != n_ok")
                    d[r["name"]] = list(r["accepted"].keys())
            lit[f"{lab.split(' ')[0]} s{s}"] = d
    dumps = {}
    for a in ("T1", "Fz"):
        for s in (0, 1, 2):
            p = reads.P("best-state/artifacts/bs/dump", f"{a}_best12_s{s}__tb72.jsonl.gz")
            rows = reads.jl(p)
            dumps[(a, s)] = rows
            d = collections.defaultdict(list)
            name_of = {}
            for r in reads.jl(reads.P("best-state/artifacts/bs/eval", f"{a}_best12_s{s}__tb72.jsonl")):
                name_of[r["prompt"]] = r["name"]
                prompts[r["name"]] = r["prompt"]
            for r in rows:
                if r.get("lean") is True:
                    d[name_of[r["prompt"]]].append(r["lean_text"])
            lit[f"bs_{a}_best12 s{s}"] = dict(d)
            # dumps must cover every solved theorem of the read
            solved = {r["name"] for r in reads.jl(reads.P("best-state/artifacts/bs/eval", f"{a}_best12_s{s}__tb72.jsonl"))
                      if r["n_ok"] > 0}
            assert solved <= set(d), (a, s, "solved theorems missing from dump", solved - set(d))

    # ---------- negative controls first ----------
    print("== negative controls")
    all_lit = [(nm, t) for d in lit.values() for nm, ts in d.items() for t in ts]
    # (a) untouched literal texts
    ctl = rng.sample(all_lit, 300)
    report("C1 untouched accepted literal texts (must all pass)", ctl, leanrc.check([(prompts[n], t) for n, t in ctl]))
    # (b) prefilter-rejected texts from the gate dumps
    rej = [(r["prompt"], r["lean_text"]) for rows in dumps.values() for r in rows if r.get("lean") is None]
    print(f"   dump rows with lean=None (prefilter rejects): {len(rej)}")
    ctl = rng.sample(rej, 600)
    report("C2 dump prefilter-rejected texts (expect all fail)", ctl, leanrc.check(ctl))
    # (c) accepted text attached to a different theorem with the same premise count
    by_np = collections.defaultdict(list)
    for nm in prompts:
        by_np[len(fml.parse_prompt(prompts[nm])[0])].append(nm)
    mis = []
    for nm, t in rng.sample(all_lit, 300):
        npm = len(fml.parse_prompt(prompts[nm])[0])
        others = [o for o in by_np[npm] if fml.parse_prompt(prompts[o]) != fml.parse_prompt(prompts[nm])]
        mis.append((prompts[rng.choice(others)], t))
    report("C3 text paired with another same-premise-count theorem (expect fail)", mis, leanrc.check(mis))
    # (d) one Or.inl/inr or .1/.2 flip
    fl = []
    for nm, t in rng.sample(all_lit, 600):
        f = flip_once(t)
        if f:
            fl.append((prompts[nm], f))
        if len(fl) >= 300:
            break
    report("C4 one Or.inl<->Or.inr / .1<->.2 flip (expect nearly all fail)", fl, leanrc.check(fl))
    # (e) sorry and truncation
    sr = [(prompts[nm], "sorry") for nm, _ in rng.sample(all_lit, 20)]
    report("C5 bare sorry (must fail)", sr, leanrc.check(sr))
    tr = []
    for nm, t in rng.sample(all_lit, 300):
        cut = t.rsplit(" ; exact ", 1)[0]
        tr.append((prompts[nm], cut))
    report("C6 final `exact` removed (must fail)", tr, leanrc.check(tr))
    cut2 = []
    for nm, t in rng.sample(all_lit, 200):
        toks = t.split(" ")
        cut2.append((prompts[nm], " ".join(toks[: max(3, int(len(toks) * rng.uniform(0.3, 0.9)))])))
    report("C7 text cut at a random token (must fail)", cut2, leanrc.check(cut2))

    # ---------- renderer validation on the dumps ----------
    print("== ND->Lean renderer validation (best-state dumps: same proof, own rendering)")
    acc_rows = [r for rows in dumps.values() for r in rows if r.get("lean") is True]
    val = rng.sample(acc_rows, 800)
    items, bad = [], 0
    for r in val:
        try:
            items.append((r["prompt"], leanrc.nd_to_lean(r["prompt"], r["nd"])))
        except leanrc.NDError:
            bad += 1
    print(f"   render failures: {bad} of {len(val)}")
    report("V1 own rendering of Lean-accepted dump proofs (expect all pass)", items, leanrc.check(items))
    rej_rows = [r for rows in dumps.values() for r in rows if r.get("lean") is None and r.get("nd")
                and not str(r["nd"]).startswith("LEANPARSE")]
    vr, badr = [], 0
    for r in rng.sample(rej_rows, min(600, len(rej_rows))):
        try:
            vr.append((r["prompt"], leanrc.nd_to_lean(r["prompt"], r["nd"])))
        except leanrc.NDError:
            badr += 1
    print(f"   prefilter-rejected rows with an ND string: {len(rej_rows)}; render failures {badr}")
    report("V2 own rendering of prefilter-rejected dump proofs (expect all fail)", vr, leanrc.check(vr))
    vf = []
    for r in rng.sample(acc_rows, 1200):
        nd = r["nd"]
        spots = [m.start() for m in re.finditer(r": ORI[12] ", nd)]
        if not spots:
            continue
        pos = rng.choice(spots)
        nd2 = nd[:pos] + (": ORI2 " if nd[pos:pos + 7] == ": ORI1 " else ": ORI1 ") + nd[pos + 7:]
        try:
            vf.append((r["prompt"], leanrc.nd_to_lean(r["prompt"], nd2)))
        except leanrc.NDError:
            pass
        if len(vf) >= 300:
            break
    report("V3 own rendering after one ORI1<->ORI2 flip in the ND (expect nearly all fail)", vf, leanrc.check(vf))

    # ---------- the real pass ----------
    print("== counted proofs, literal text (one per solved theorem + random fill to >= 150 per arm-seed)")
    totals = collections.Counter()
    for lab, d in lit.items():
        samp = sample_cover(d, True, 150)
        res = leanrc.check([(prompts[n], t) for n, t in samp])
        a, n = report(f"{lab} ({len(d)} solved theorems)", samp, res)
        totals[lab.rsplit(" ", 1)[0] + " acc"] += a
        totals[lab.rsplit(" ", 1)[0] + " n"] += n
        for (nm, t), (ok, why) in zip(samp, res):
            if not ok:
                print(f"   REJECTED {lab} {nm}: {why} :: {t[:200]}")
    print("== counted proofs, ND only (own rendering): one per solved theorem + random fill to >= 150 per arm-seed")
    for lab in ["rc_r16_plain_x1"] + [f"gb_{a}_r8_{x}" for a in ("default", "passk", "unlikely") for x in ("x0", "x1")]:
        for s, (p, _) in reads.arms()[lab].items():
            d = {}
            for r in reads.jl(p):
                prompts[r["name"]] = r["prompt"]
                if r["n_ok"] > 0:
                    assert r["proofs"], (p, r["name"])
                    d[r["name"]] = r["proofs"]
            samp = sample_cover(d, True, 150)
            items, fails = [], []
            for nm, nd in samp:
                try:
                    items.append((prompts[nm], leanrc.nd_to_lean(prompts[nm], nd)))
                except leanrc.NDError as e:
                    fails.append((nm, str(e)))
            res = leanrc.check(items)
            a, n = report(f"{lab} s{s} ({len(d)} solved) [render fails {len(fails)}]", items, res)
            for (pr, t), (ok, why) in zip(items, res):
                if not ok:
                    print(f"   REJECTED {lab} s{s}: {why} :: {pr} :: {t[:200]}")
            for f in fails:
                print("   RENDER-FAIL", lab, s, f)
            totals[lab + " acc"] += a
            totals[lab + " n"] += n
    print("== totals")
    for k in sorted({k.rsplit(" ", 1)[0] for k in totals}):
        print(f"   {k:<40} {totals[k + ' acc']}/{totals[k + ' n']}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Reviewer (coe-dose01): Lean re-check of the counted held-out proofs from their stored LITERAL text.

Population per ladder: every distinct literal text in the ladder's LEAN_GATE_DUMP whose prompt is a strict member and that
the run recorded as Lean-accepted; each is joined to its first-found round through the ND string (dump 'nd' ==
found_transfer 'proof').  Re-derived y_lean(r) = strict members with a literal text accepted by MY harness whose ND proof
was first found in round <= r.  (knockout s1: the dump covers rounds 25-32 only; earlier members are covered by the
create-or-elicit review.)

Controls first (all on the same harness): untouched counted texts (must pass), statement swap (text paired with another
strict member with the same premise count: must fail), Or.inl<->Or.inr / .1<->.2 flips (nearly all fail), sorry
(must fail), prefilter-rejected texts (expected to fail; any pass = a filter false reject, which can only LOWER counts).

  python3 recheck.py controls | full
"""
import collections, json, random, re, sys
sys.path.insert(0, '/home/dan/work/coe-dose01/review_cd01')
from common import BIG, REPO, jl, strict_members, seq_of_prompt
import leanrc

LADS = {'la_dose01_s0': 'la_dose01_s0', 'la_dose01_s1': 'la_dose01_s1', 'la_dose01_s2': 'la_dose01_s2', 'la_ko_s1': 'la_ko_s1_r25-32'}


def load(lad):
    ft = collections.defaultdict(dict)        # prompt -> nd -> round
    for x in jl(f'{BIG}/ft/{lad}_strict.jsonl.gz'):
        ft[x['prompt']][x['proof']] = x['round']
    dump = [x for x in jl(f"{BIG}/dump/{LADS[lad]}_strict.jsonl.gz")]
    acc = {}
    for x in dump:
        if x.get('lean') is True:
            acc[(x['prompt'], x['lean_text'])] = (x['name'], x['nd'])
    return ft, dump, acc


def flip(t):
    for a, b in (('Or.inl', 'Or.inr'), ('Or.inr', 'Or.inl'), ('.1 ', '.2 '), ('.2 ', '.1 ')):
        i = t.find(a)
        if i >= 0:
            return t[:i] + b + t[i + len(a):]
    return None


def controls():
    rng = random.Random(7)
    pos, swap, flips, filt = [], [], [], []
    tr = {r['name']: r for r in jl(f'{REPO}/data/coe/transfer_track832.jsonl')}
    SM = strict_members()
    by_np = collections.defaultdict(list)
    for n in SM:
        by_np[len(seq_of_prompt(tr[n]['prompt'])[0])].append(tr[n]['prompt'])
    for lad in LADS:
        ft, dump, acc = load(lad)
        items = sorted(acc)
        rng.shuffle(items)
        pos += items[:60]
        for (p, t) in items[60:110]:
            np_ = len(seq_of_prompt(p)[0])
            others = [q for q in by_np[np_] if q != p]
            if others:
                swap.append((rng.choice(others), t))
        for (p, t) in items[110:200]:
            f = flip(t)
            if f:
                flips.append((p, f))
        fr = [(x['prompt'], x['lean_text']) for x in dump if x.get('filter')]
        rng.shuffle(fr)
        filt += fr[:60]
    sorry = [(p, 'sorry') for p, _ in pos[:20]]
    res = {}
    for name, items, want in (('untouched', pos, True), ('statement_swap', swap, False), ('flip', flips, False),
                              ('sorry', sorry, False), ('prefilter_rejected', filt, False)):
        r = leanrc.check(items)
        npass = sum(ok for ok, _ in r)
        res[name] = dict(n=len(items), passed=npass, expect='all pass' if want else 'fail',
                         reasons=dict(collections.Counter(w for _, w in r)))
        print(f'control {name}: {npass}/{len(items)} passed (expected {"all" if want else "none / few"}); reasons {res[name]["reasons"]}', flush=True)
        if name == 'flip':
            res[name]['passing_examples_masked'] = [re.sub(r'[PQRS]', 'X', items[i][0])[:80] for i, (ok, _) in enumerate(r) if ok][:5]
    json.dump(res, open(f'{REPO}/review_cd01/out/recheck_controls.json', 'w'), indent=1)


def full():
    out = {}
    SM = strict_members()
    tr = {r['name']: r for r in jl(f'{REPO}/data/coe/transfer_track832.jsonl')}
    p2n = {tr[n]['prompt']: n for n in SM}
    for lad in LADS:
        ft, dump, acc = load(lad)
        items = sorted(acc)
        r = leanrc.check(items)
        ok = {it: o for it, (o, _) in zip(items, r)}
        rej = [(acc[it][0], why) for it, (o, why) in zip(items, r) if not o]
        # join to rounds
        joined = 0; first = {}
        unjoined = 0
        for (p, t), o in ok.items():
            nd = acc[(p, t)][1]
            rd = ft.get(p, {}).get(nd)
            if rd is None:
                unjoined += 1
                continue
            joined += 1
            if o:
                n = p2n[p]
                first[n] = min(first.get(n, 99), rd)
        # found_transfer rows of strict members that have NO accepted literal text in the dump
        nd_with_text = {(p, acc[(p, t)][1]) for (p, t) in acc}
        ft_rows = [(p, nd, rd) for p, d in ft.items() for nd, rd in d.items()]
        no_text = [(p2n[p], rd) for p, nd, rd in ft_rows if (p, nd) not in nd_with_text]
        last = 32 if lad == 'la_ko_s1' else 16
        lo = 25 if lad == 'la_ko_s1' else 1
        y_lean = {r_: sum(1 for n, fr in first.items() if fr <= r_) for r_ in range(lo, last + 1)}
        out[lad] = dict(texts=len(items), accepted=sum(ok.values()), rejected=rej[:50], n_rejected=len(rej),
                        joined_to_round=joined, unjoined=unjoined, ft_rows=len(ft_rows),
                        ft_rows_without_dump_text=len(no_text), ft_rows_without_dump_text_rounds=dict(collections.Counter(rd for _, rd in no_text)),
                        y_lean=y_lean, members_lean=sorted(first))
        print(f"{lad}: {sum(ok.values())}/{len(items)} literal texts accepted by my harness; joined to a round {joined}, unjoined {unjoined}; "
              f"found_transfer strict rows without a dump text {len(no_text)} (rounds {out[lad]['ft_rows_without_dump_text_rounds']}); "
              f"y_lean {y_lean}", flush=True)
    json.dump(out, open(f'{REPO}/review_cd01/out/recheck_full.json', 'w'), indent=1)


if __name__ == '__main__':
    {'controls': controls, 'full': full}[sys.argv[1]]()

#!/usr/bin/env python3
"""Reviewer: classify every distinct accepted proof in one ladder found file (cumulative; each proof carries the round
it was first found) -- per round: new distinct proofs, with DN, sigma (DN on a NEGI line), sigma+ (DN on any derived line),
sigma_impi (DN on an IMPI line, Lean-only spelling), lemma route, and FREE POSITIVE reductio = a DN step on a derived
line whose conclusion G is not a negation and whose double negation ~~G does not occur in the sequent (the genuinely
classical step).  Per strict trained / held-out member: first round solved, first round with a free positive reductio.
  python3 found.py FILE.jsonl LABEL [targets|transfer]  -> review_coe/found/<LABEL>.json"""
import collections, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

RV = C.RV
FAM = json.load(open(f'{RV}/review_coe/out_families.json'))
STRICT = set(FAM['strict_trained']) | set(FAM['strict_heldout'])
fn, label = sys.argv[1], sys.argv[2]
kind = sys.argv[3] if len(sys.argv) > 3 else 'targets'
RX = re.compile(r'"round": (\d+)')


def free_pos(nd, prompt):
    """list of (dn_idx, cited_rule) for DN steps on a derived line with non-negated conclusion G and ~~G absent from the
    sequent (semantically: no subformula (G -> F) -> F)."""
    L = C.parse_nd(nd)
    pos = {x[0]: i for i, x in enumerate(L)}
    prem, concl = C.split_prompt(prompt)
    subs = set()
    for s in prem + [concl]:
        subs.update(C.subformulas(C.parse(s)))
    out = []
    for idx, d, f, rule, refs in L:
        if rule != 'DN' or not refs:
            continue
        o = C.origin(L, pos, refs[0]); cr = L[pos[o]][3]
        if cr in ('PR', 'AS'):
            continue
        g = C.parse(f)
        if g[0] == '>' and g[2] == C.FALSE:        # conclusion is a negation: intuitionistically fine (~~~X -> ~X)
            continue
        if ('>', ('>', g, C.FALSE), C.FALSE) in subs:
            continue
        out.append((idx, cr))
    return out


per = collections.defaultdict(collections.Counter)
first_solved = {}; first_free = {}; first_sp = {}
examples = []
n = 0
with open(fn) as f:
    for l in f:
        n += 1
        m = RX.search(l)
        r = int(m.group(1))
        c = per[r]
        c['new'] += 1
        name = None
        if '"name": "' in l:
            i = l.index('"name": "') + 9; name = l[i:l.index('"', i)]
        if name in STRICT:
            c['new_strict'] += 1
            first_solved[name] = min(first_solved.get(name, 99), r)
        if ': DN ' not in l:
            continue
        x = json.loads(l)
        fl = C.sigma_flags(x['proof'])
        c['dn'] += 1
        for k in ('sigma', 'sigma_plus', 'sigma_impi', 'lemma', 'lemma_broad', 'dn_pr_as_only'):
            if fl[k]:
                c[k] += 1
        fp = free_pos(x['proof'], x['prompt'])
        if fp:
            c['free_pos'] += 1
            for _, cr in fp:
                c['free_pos_cited:' + cr] += 1
            if name in STRICT:
                c['free_pos_strict'] += 1
                first_free[name] = min(first_free.get(name, 99), r)
            if len(examples) < 40:
                examples.append({'round': r, 'name': name, 'prompt': x['prompt'], 'proof': x['proof'], 'cited': [cr for _, cr in fp]})
        if fl['sigma_plus'] and name in STRICT:
            first_sp[name] = min(first_sp.get(name, 99), r)
        if fl['sigma_plus']:
            c['sp_any_target'] += 1
out = {'file': fn, 'kind': kind, 'lines': n, 'per_round': {r: dict(per[r]) for r in sorted(per)},
       'first_solved_strict': first_solved, 'first_free_pos_strict': first_free, 'first_sigma_plus_strict': first_sp,
       'first_round_sigma_plus_any': min((r for r in per if per[r]['sigma_plus']), default=None),
       'first_round_free_pos_any': min((r for r in per if per[r]['free_pos']), default=None),
       'examples': examples}
os.makedirs(f'{RV}/review_coe/found', exist_ok=True)
json.dump(out, open(f'{RV}/review_coe/found/{label}.json', 'w'), indent=1)
print(label, 'lines', n, 'first sigma+', out['first_round_sigma_plus_any'], 'first free+', out['first_round_free_pos_any'],
      'strict solved', len(first_solved), 'strict with free+', len(first_free))
for r in sorted(per):
    c = per[r]
    print(f'  r{r:2d} new {c["new"]:7d} dn {c["dn"]:6d} sigma {c["sigma"]:6d} sigma+ {c["sigma_plus"]:6d} impi {c["sigma_impi"]:4d} '
          f'lemma {c["lemma"]:3d}/{c["lemma_broad"]:3d} free+ {c["free_pos"]:5d} (strict {c["free_pos_strict"]:4d}) new_strict {c["new_strict"]:5d}')

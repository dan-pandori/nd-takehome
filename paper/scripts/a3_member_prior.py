"""A3 (pre-registered; Addendum 1 extensions exploratory): does the base's likelihood of a member's best known sigma proof
predict which strict held-out members a ladder solves at r16?

Inputs (bucket hf://buckets/dan-pandori/nd-rl/create-or-elicit/artifacts/coe/, fetched one at a time under a flock into
~/runs/create-or-elicit-paper/scratch/coe/, not in git):
  score/known_b1/{full_s0}.jsonl.gz + targets.jsonl.gz          pend scores, old full s0 (one name base, T 0.8)
  score/rounds_{arm}_s{S}/pend.jsonl.gz + targets.jsonl.gz       pend scores, full s3-s5 and dose s0-s2
  eval/r16_{arm}_s{S}_x0*.jsonl.gz                               the r16 plain x0 read rows (old seeds: x0e + x0h)
Members: strict held-out (data/coe/sigma_heldout_strict.txt) with >= 1 known sigma proof (101).
Output: paper/data/a3_member_prior.json and a printed table.
"""
import gzip, json, os, subprocess, sys, collections

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SCR = os.path.expanduser('~/runs/create-or-elicit-paper/scratch/coe')
BK = 'hf://buckets/dan-pandori/nd-rl/create-or-elicit/artifacts/coe'
os.makedirs(SCR, exist_ok=True)


def fetch(rel, local):
    p = os.path.join(SCR, local)
    if not os.path.exists(p) or os.path.getsize(p) == 0:
        subprocess.run(['flock', '/tmp/coep_dl.lock', 'hf', 'buckets', 'cp', f'{BK}/{rel}', p], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return p


def jl(p):
    with gzip.open(p, 'rt') as f:
        for line in f:
            yield json.loads(line)


strict = [l.strip() for l in open(os.path.join(ROOT, 'data/coe/sigma_heldout_strict.txt')) if l.strip()]
fam_of = {}
fams = json.load(open(os.path.join(ROOT, 'data/coe/families.json')))['families']
for f, v in fams.items():
    for m in v.get('heldout', []):
        fam_of[m['name']] = f
fam_of.setdefault('la_transfer_916', 'generated')

LADDERS = [('full', 0), ('full', 3), ('full', 4), ('full', 5), ('dose1', 0), ('dose1', 1), ('dose1', 2)]


def best_pend_logp(arm, s):
    if arm == 'full' and s == 0:
        sp = fetch('score/known_b1/full_s0.jsonl.gz', 'kb1_full_s0.jsonl.gz')
        tp = fetch('score/known_b1/targets.jsonl.gz', 'kb1_targets.jsonl.gz')
    else:
        sp = fetch(f'score/rounds_{arm}_s{s}/pend.jsonl.gz', f'score_{arm}_s{s}_pend.jsonl.gz')
        tp = fetch(f'score/rounds_{arm}_s{s}/targets.jsonl.gz', f'targets_rounds_{arm}_s{s}.jsonl.gz')
    name = {r['tid']: r['name'] for r in jl(tp)}
    best = {}
    for r in jl(sp):
        if arm == 'full' and s == 0 and r.get('ckpt') not in (None, 'pend', 'full_s0'):
            pass
        t = r['T0.8']['total'] if isinstance(r['T0.8'], dict) else None
        n = name.get(r['tid'])
        if n is None or t is None:
            continue
        best[n] = max(best.get(n, -1e9), t)
    return best


def r16_solved(arm, s):
    tags = [f'r16_{arm}_s{s}_x0e', f'r16_{arm}_s{s}_x0h'] if (arm == 'full' and s < 3) else [f'r16_{arm}_s{s}_x0']
    solved = collections.defaultdict(bool)
    for tg in tags:
        for r in jl(fetch(f'eval/{tg}.jsonl.gz', f'{tg}.jsonl.gz')):
            solved[r['name']] |= bool(r.get('n_ok', 0) > 0 or r.get('solved'))
    return solved


def auc(pos, neg):
    if not pos or not neg:
        return None
    w = sum((1.0 if p > q else 0.5 if p == q else 0.0) for p in pos for q in neg)
    return w / (len(pos) * len(neg))


def within_family_auc(rows):
    w = n = 0.0
    byf = collections.defaultdict(list)
    for m, lp, y in rows:
        byf[fam_of.get(m, '?')].append((lp, y))
    for f, xs in byf.items():
        pos = [lp for lp, y in xs if y]; neg = [lp for lp, y in xs if not y]
        for p in pos:
            for q in neg:
                w += 1.0 if p > q else 0.5 if p == q else 0.0; n += 1
    return (w / n if n else None), int(n)


out = {}
values = {}
for arm, s in LADDERS:
    lp = best_pend_logp(arm, s)
    sol = r16_solved(arm, s)
    rows = [(m, lp[m], sol.get(m, False)) for m in strict if m in lp]
    values[f'{arm}_s{s}'] = {m: {'logp': x, 'solved_r16': y, 'family': fam_of.get(m, '?')} for m, x, y in rows}
    pos = [x for _, x, y in rows if y]; neg = [x for _, x, y in rows if not y]
    a = auc(pos, neg); wf, npairs = within_family_auc(rows)
    out[f'{arm}_s{s}'] = {'members_with_known': len(rows), 'solved_r16': len(pos), 'auc': a, 'within_family_auc': wf,
                          'within_family_pairs': npairs, 'solved_in_strict106': sum(1 for m in strict if sol.get(m))}
    print(f'{arm}_s{s}: members {len(rows)}, solved {len(pos)} (all strict: {out[f"{arm}_s{s}"]["solved_in_strict106"]}), '
          f'AUC {a:.3f}, within-family AUC {wf:.3f} over {npairs} pairs')
json.dump(out, open(os.path.join(ROOT, 'paper/data/a3_member_prior.json'), 'w'), indent=1)
json.dump(values, open(os.path.join(ROOT, 'paper/data/a3_member_values.json'), 'w'), indent=0)

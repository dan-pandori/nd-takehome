#!/usr/bin/env python3
"""Lean re-check of counted proofs from their stored LITERAL text (reviewer harness rlean.py, Lean 4.34.1 = the pods'
version), per arm, with negative controls run in the same harness:
  untouched counted proofs (must pass) / first Or.inl<->Or.inr flipped (nearly all must fail) / text paired with another
  theorem with the same premise count (must fail) / `exact sorry` (must fail on the axioms check) / texts the run's
  prefilter rejected before Lean (LEAN_GATE_DUMP rows with filter set; expected to fail -- a pass is a filter false reject).
Sources: eval rows' `accepted` texts, free rows' `text` (valid rows), the ladder dumps' Lean-accepted texts.
Reservoir-sampled, seed 20261020; textbook72 proofs are checked like any other but never printed.

  python3 review_kal/recheck.py [--per_arm 150] -> out/recheck.json
"""
import argparse, collections, glob, json, os, random, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kc, rlean

ap = argparse.ArgumentParser()
ap.add_argument('--per_arm', type=int, default=150)
ap.add_argument('--n_rej', type=int, default=300)
a = ap.parse_args()
A = os.path.join(kc.ROOT, 'artifacts', 'kalmar')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
rng = random.Random(20261020)


class Res:
    def __init__(self, n):
        self.n, self.seen, self.items = n, 0, []

    def add(self, x):
        self.seen += 1
        if len(self.items) < self.n:
            self.items.append(x)
        else:
            j = rng.randrange(self.seen)
            if j < self.n:
                self.items[j] = x


def arm_of(model):
    for p, arm in (('ctl_', 'control'), ('kalC_', 'KAL-C'), ('kalDA_', 'KAL-D+A'), ('kalD_', 'KAL-D'), ('la_kal_ei', 'EI r1/r2 greedy')):
        if model.startswith(p):
            return arm
    return None


R = collections.defaultdict(lambda: Res(a.per_arm))
inputs = {}
for fn in sorted(glob.glob(os.path.join(A, 'eval', '*.rows.jsonl.gz'))):
    model = os.path.basename(fn)
    arm = arm_of(model)
    for r in kc.rows(fn):
        for t in r['accepted']:
            R[arm].add((r['prompt'], t, os.path.basename(fn), r['file']))
for fn in sorted(glob.glob(os.path.join(A, 'free', '*.rows.jsonl.gz'))):
    model = os.path.basename(fn).split('__')[0]
    arm = arm_of(model)
    summ = json.load(open(fn.replace('.rows.jsonl.gz', '.json')))
    if summ['in'] not in inputs:
        inputs[summ['in']] = [x['prompt'] for x in kc.rows(os.path.join(kc.ROOT, summ['in']))]
    pr = inputs[summ['in']]
    for r in kc.rows(fn):
        if r['valid']:
            R[arm].add((pr[r['i']], r['text'], os.path.basename(fn), summ['in']))
rej = Res(a.n_rej)
for lab, fn in (('EI ladder (dump)', 'la_kal_ei_s0'), ('frozen ladder (dump)', 'la_kal_frozen_s0')):
    for r in kc.rows(os.path.join(A, 'dump', fn + '.jsonl.gz')):
        if r.get('lean') is True:
            R[lab].add((r['prompt'], r['lean_text'], fn, 'ladder'))
        elif r.get('filter') is not None:
            rej.add((r['prompt'], r['lean_text'], fn, r['filter']))
print({k: (v.seen, len(v.items)) for k, v in R.items()}, 'rejects seen', rej.seen, flush=True)

res = {'per_arm': {}, 'controls': {}}
t0 = time.time()
allc = []
for arm, rs in sorted(R.items()):
    out = rlean.check_robust([(p, t) for p, t, src, st in rs.items])
    fails = [(rs.items[i][2], rs.items[i][3], info) for i, (ok, info, sz) in enumerate(out) if not ok]
    res['per_arm'][arm] = {'pool': rs.seen, 'checked': len(out), 'accepted': sum(ok for ok, info, sz in out), 'fails': fails}
    print(arm, res['per_arm'][arm]['accepted'], '/', len(out), 'pool', rs.seen, 'fails', fails[:3], round(time.time() - t0), 's', flush=True)
    allc += rs.items

# controls
def flip(t):
    m = re.search(r'Or\.inl|Or\.inr', t)
    if not m:
        return None
    rep = 'Or.inr' if m.group(0) == 'Or.inl' else 'Or.inl'
    return t[:m.start()] + rep + t[m.end():]


sub = rng.sample(allc, min(300, len(allc)))
fl = [(p, flip(t)) for p, t, s, st in sub if flip(t)]
out = rlean.check_robust(fl)
res['controls']['flip_first_or_intro'] = {'n': len(out), 'passed': sum(ok for ok, i, z in out)}
by_np = collections.defaultdict(list)
for p, t, s, st in allc:
    by_np[len(kc.split_prompt(p)[0])].append((p, t))
mis = []
for p, t, s, st in sub[:200]:
    cands = [q for q, u in by_np[len(kc.split_prompt(p)[0])] if q != p]
    if cands:
        mis.append((rng.choice(cands), t))
out = rlean.check_robust(mis)
res['controls']['mismatched_theorem'] = {'n': len(out), 'passed': sum(ok for ok, i, z in out)}
out = rlean.check_robust([(p, 'exact sorry') for p, t, s, st in sub[:30]])
res['controls']['sorry'] = {'n': len(out), 'passed': sum(ok for ok, i, z in out), 'infos': sorted({i for ok, i, z in out})}
out = rlean.check_robust([(p, t) for p, t, s, st in rej.items])
passed = [(rej.items[i][2], rej.items[i][3]) for i, (ok, info, sz) in enumerate(out) if ok]
res['controls']['prefilter_rejects'] = {'pool': rej.seen, 'n': len(out), 'passed_in_lean': len(passed), 'passed': passed[:20],
                                        'reasons': dict(collections.Counter(x[3] for x in rej.items).most_common())}
print(json.dumps(res['controls']), round(time.time() - t0), 's', flush=True)
json.dump(res, open(os.path.join(OUT, 'recheck.json'), 'w'), indent=1)

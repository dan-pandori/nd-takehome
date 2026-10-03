#!/usr/bin/env python3
"""Reviewer recount (mcts-a), part 2: Lean 4 core re-check of counted proofs.
  search arms (prior / value, every read-out, tuning and x10): EVERY solved tree's stored literal lean_seq `text`, wrapped
    as `theorem t (P Q R S : Prop) (h_i : prem_i) : goal := by <text>`; plus a scan for tactics outside the grammar.
  sample arm: state_eval keeps the env's ND string, not the literal text -> my own ND -> Lean translator (rlean.translate,
    reviewer-owned): one random accepted proof per solved theorem per job, plus every proof on group C.
  negative controls: (a) the sample rows' stored LEANREJ fail examples (ND, Lean-rejected by the gate) through the same
    translator; (b) 200 search texts with the goal replaced by `False` (must all fail).
Output: r2_lean.json"""
import json, os, glob, random, re, collections, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import rlean
W = os.path.expanduser('~/review/mcts-a'); E = f'{W}/artifacts/mcts'
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
BAD = re.compile(r'\b(sorry|admit|decide|tauto|simp|omega|aesop|native_decide|exact\?|apply\?|trivial|assumption|contradiction|cases|rcases|intro|by_cases|first|repeat|all_goals|sorryAx|Classical\.em|Decidable)\b')
rng = random.Random(20261003)

def lit(prompt, text, nm, goal=None):
    prem, c = rlean.parse_prompt(prompt)
    hs = ''.join(f' (h{k + 1} : {rlean.lf(p)})' for k, p in enumerate(prem))
    return f'theorem {nm} (P Q R S : Prop){hs} : {goal or rlean.lf(c)} := by {text}'

srch, smp, neg = [], [], []
for f in sorted(glob.glob(f'{E}/eval/*.jsonl') + glob.glob(f'{E}/eval_x10/*.jsonl')):
    lab = os.path.relpath(f, E)[:-6]; arm = lab.rsplit('__', 1)[1]
    for r in rd(f):
        if arm.startswith('sample'):
            if r['solved']:
                ps = r['proofs'] if '__C__' in lab else [rng.choice(r['proofs'])]
                smp += [(lab, r['prompt'], p) for p in ps]
            fe = r.get('fail_example') or ''
            if fe.startswith('LEANREJ '):
                neg.append((lab, r['prompt'], fe[len('LEANREJ '):]))
        elif r['solved']:
            srch.append((lab, r['prompt'], r['text']))
out = {}
toks = collections.Counter(m.group(1) for _, _, t in srch for m in BAD.finditer(t))
out['search_bad_tokens'] = dict(toks)

def tally(items, res):
    by = collections.defaultdict(lambda: [0, 0]); fails = []
    for (lab, p, x), (ok, why) in zip(items, res):
        a = re.sub(r'^eval(_x10)?/s\d_(pend|r8)__\w+?__', '', lab).replace('_t', ' t')
        a = ('x10 ' if 'x10' in lab else '') + a.split(' ')[0]
        by[a][0] += 1; by[a][1] += ok
        if not ok: fails.append(dict(job=lab, prompt=p, proof=x[:400], why=why))
    return dict(by), fails

r = rlean.check([(p, t) for _, p, t in srch], lambda p, t, nm: lit(p, t, nm))
out['search'], out['search_fail'] = tally(srch, r)
print('search', out['search'], len(out['search_fail']), flush=True)
r = rlean.check([(p, x) for _, p, x in smp], rlean.translate)
out['sample'], out['sample_fail'] = tally(smp, r)
print('sample', out['sample'], len(out['sample_fail']), flush=True)
ng = rng.sample(neg, min(300, len(neg)))
r = rlean.check([(p, x) for _, p, x in ng], rlean.translate)
out['neg_leanrej'] = dict(n=len(ng), lean_ok=sum(ok for ok, _ in r),
                          ok_examples=[x[:300] for (_, _, x), (ok, _) in zip(ng, r) if ok][:5])
ns = rng.sample(srch, min(200, len(srch)))
r = rlean.check([(p, t) for _, p, t in ns], lambda p, t, nm: lit(p, t, nm, goal='False'))
out['neg_goal_false'] = dict(n=len(ns), lean_ok=sum(ok for ok, _ in r))
print('neg', out['neg_leanrej']['n'], out['neg_leanrej']['lean_ok'], out['neg_goal_false'], flush=True)
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'r2_lean.json'), 'w'), indent=1)

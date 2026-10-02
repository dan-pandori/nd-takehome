#!/usr/bin/env python3
"""organism-analysis Q2 gallery (rule fixed in preregistration/organism-analysis.md before looking):
  * for each of the 6 most frequent hard-step classes (pooled c12 + c6), for c12 and c6: the seed-0 group-B theorem
    (x0 read: r0 fails, r8 solves) whose hard step of that class has the median gain r0 -> r8 among such theorems
    (lower median when even);
  * for the 4 most frequent classes: the c12 seed-0 never-solved theorem (no read r1..r8 solves) with the median gain.
Each: the reference proof in Lean (nd2lean), one line per environment action, with per-step log p (nats, T 1.0) at r0
and r8; for B also r8's eventual proof.  Writes organism/gallery.md and artifacts/oa/gallery.json.
"""
import collections, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from oa_load import ROOT, read_both, score, targets_meta
import nd2lean

S = [json.loads(l) for l in open('data/oa/q2_steps.jsonl')]
H = [s for s in S if s['hard'] and s['run'] in ('c12', 'c6')]
top = [k for k, _ in collections.Counter(s['cls'] for s in H).most_common(6)]
inputs = {}
for run, d in (('c12', 'tj'), ('c6', 'tj6')):
    for l in open(os.path.join(ROOT, d, 'targets', 'targets_s0.jsonl')):
        t = json.loads(l); inputs[(run, t['tid'])] = t


def groupB(run):
    r0, r8 = read_both(run, 's0_pend', 0), read_both(run, 's0_r8', 0)
    return {n for n in r0 if r0[n][0] == 0 and r8[n][0] > 0}


def pick(run, cls, status_fn):
    per = {}
    for s in H:
        if s['run'] == run and s['seed'] == 0 and s['cls'] == cls and status_fn(s):
            g = s['lp'][8] - s['lp'][0]
            if s['name'] not in per or s['lp'][0] < per[s['name']][1]['lp'][0]:   # the theorem's worst hard step of the class
                per[s['name']] = (g, s)
    if not per:
        return None
    items = sorted(per.values(), key=lambda v: (v[0], v[1]['name']))
    return items[(len(items) - 1) // 2][1], len(items)


def render(run, tid, ck0='pend', ck8='r8', hard_i=None):
    t = inputs[(run, tid)]
    src = nd2lean.translate(t['prompt'], t['proof'], require_all_pr=False).split('\n')
    a, b = score(run, 0, ck0)[tid]['step_lp'], score(run, 0, ck8)[tid]['step_lp']
    src = [l for l in src if l.strip()]
    body = src[1:]
    out = [src[0]]
    if len(body) != len(a):
        return '\n'.join(src) + f'\n-- (per-step log p r0 / r8: {[round(x, 2) for x in a]} / {[round(x, 2) for x in b]})'
    w = max(len(x) for x in body)
    for i, (ln, x, y) in enumerate(zip(body, a, b)):
        mark = '  ◀ hard step' if i == hard_i else ''
        out.append(f'{ln:<{w}}  -- r0 {x:6.2f} → r8 {y:6.2f}{mark}')
    return '\n'.join(out)


def main():
    B = {run: groupB(run) for run in ('c12', 'c6')}
    ex = []
    for cls in top:
        for run in ('c12', 'c6'):
            p = pick(run, cls, lambda s, run=run: s['name'] in B[run])
            if p:
                ex.append(('B', run, cls, p[0], p[1]))
    for cls in top[:4]:
        p = pick('c12', cls, lambda s: s['status'] == 'never')
        if p:
            ex.append(('never', 'c12', cls, p[0], p[1]))
    md = ['# Gallery: hard steps before and after RL (organism-analysis)', '',
          'Selection rule (pre-registered): per hard-step class, the median-gain seed-0 theorem; see `oa/oa_gallery.py`.',
          'Models: **c12** = best-cap12 seed 0, **c6** = best-cap6 seed 0 (ALiBiGPT 6 × 384, 9,560,832 params, `lean_staten`,',
          'from scratch; r0 = end of pretraining, r8 = after 8 EI rounds; `trajectory` / `trajectory-cap6` checkpoints).',
          'Per-step log p: nats, T 1.0, teacher-forced in the proof-state environment, marginalised over name bases',
          '(`tj_score`). One Lean line per environment action. Reference = a shortest known ND proof (`minlen`; ND-derived',
          'length labels are upper bounds under Lean). Lean alone judges every counted proof; these renderings are',
          '`nd2lean` translations of Lean-accepted proofs (`trajectory`: 896 / 896 targets Lean-accepted).', '']
    rows = []
    for k, (kind, run, cls, s, n) in enumerate(ex, 1):
        tid = 'ref:' + s['name']
        g = s['lp'][8] - s['lp'][0]
        md += [f'## {k}. {cls} — {run}, {"group B (solved by RL)" if kind == "B" else "never solved r1–r8"} — `{s["name"]}`', '',
               f'Hard step {s["i"] + 1}: r0 {s["lp"][0]:.2f} → r8 {s["lp"][8]:.2f} nats (gain {g:+.2f}; median of {n} such theorems).', '',
               'Reference proof:', '', '```lean', render(run, tid, hard_i=s['i']), '```', '']
        rows.append({'k': k, 'kind': kind, 'run': run, 'cls': cls, 'name': s['name'], 'step': s['i'], 'lp0': s['lp'][0],
                     'lp8': s['lp'][8], 'n_candidates': n})
        if kind == 'B' and (run, 'ev:' + s['name']) in inputs:
            ev = 'ev:' + s['name']
            e8 = score(run, 0, 'r8')[ev]
            md += [f'Eventual proof (r8\'s most likely accepted sample; worst step r0 {score(run, 0, "pend")[ev]["w1"]:.2f} → r8 {e8["w1"]:.2f}):', '',
                   '```lean', render(run, ev, hard_i=e8['w1_idx']), '```', '']
    os.makedirs('organism', exist_ok=True)
    open('organism/gallery.md', 'w').write('\n'.join(md) + '\n')
    json.dump({'classes': top, 'examples': rows}, open('artifacts/oa/gallery.json', 'w'), indent=1)
    print(f'{len(rows)} examples; classes {top}')


if __name__ == '__main__':
    main()

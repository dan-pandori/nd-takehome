#!/usr/bin/env python3
"""trajectory: target proofs for teacher-forced scoring (tj_score.py).  Pure python (runs on the VPS or a pod).

  python3 tj_targets.py refs                       -> data/tj/ref_targets.jsonl
  python3 tj_targets.py cands  --seed S            -> data/tj/cand_sS.jsonl      (r8's distinct accepted seed-0 samples)
  python3 tj_targets.py select --seed S            -> data/tj/targets_sS.jsonl   (refs + eventual proofs) and
                                                      data/tj/eventual_sS.jsonl (the choice, with its runner-up count)

Reference proof (preregistration/trajectory.md): holdout250 -> ladder-A's minlen label (`data/tj/ref_h250.jsonl`);
textbook72 -> `minlen.py` on the 72 prompts here (`data/tj/tb72_minlen.jsonl`, bound 14, then `tb72_minlen22.jsonl`,
bound 22, for the 15 it left unlabelled).  Theorems with no minlen proof have no reference (reported).
Eventual proof: among r8's distinct Lean-accepted samples at k 256, sampling seed 0 (`artifacts/tj/eval/s<S>_r8__<pool>_x0.jsonl`,
field `proofs`), the one with the highest log p (T 1.0, base-marginalised) under r8 (`artifacts/tj/score/cand_s<S>/s<S>_r8.jsonl`).
Ties: fewer steps, then the ND string.
"""
import argparse, json, os

POOLS = {'tb72': 'data/bs/textbook72.jsonl', 'h250': 'data/bs/holdout250.jsonl'}


def rj(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def wj(p, rows):
    with open(p, 'w') as f:
        for r in rows:
            f.write(json.dumps(r) + '\n')


def refs():
    tb = rj(POOLS['tb72'])
    ml = {}
    for p in ('data/tj/tb72_minlen22.jsonl', 'data/tj/tb72_minlen.jsonl'):     # bound-14 label wins where both exist
        if os.path.exists(p):
            for r in rj(p):
                if r.get('proof'):
                    ml[r['prompt']] = dict(r, ref_source=f'minlen {os.path.basename(p)} (bound {r.get("bound")})')
    out, miss = [], []
    for r in tb:
        m = ml.get(r['prompt'])
        if m is None:
            miss.append(r['name']); continue
        out.append({'tid': 'ref:' + r['name'], 'name': r['name'], 'pool': 'tb72', 'prompt': r['prompt'], 'kind': 'ref',
                    'proof': m['proof'], 'ref_source': m['ref_source'], 'min_lines_ub': m.get('min_lines_ub')})
    for r in rj('data/tj/ref_h250.jsonl'):
        out.append({'tid': 'ref:' + r['name'], 'name': r['name'], 'pool': 'h250', 'prompt': r['prompt'], 'kind': 'ref',
                    'proof': r['proof'], 'ref_source': r['ref_source'], 'min_lines_ub': r.get('min_lines_ub')})
    wj('data/tj/ref_targets.jsonl', out)
    print(f'refs: {len(out)} (tb72 {sum(o["pool"] == "tb72" for o in out)}/72, h250 {sum(o["pool"] == "h250" for o in out)}/250); '
          f'textbook72 without a reference: {len(miss)} {miss}')


def cands(s):
    out = []
    for pool in POOLS:
        for r in rj(f'artifacts/tj/eval/s{s}_r8__{pool}_x0.jsonl'):
            for i, p in enumerate(sorted(set(r['proofs']))):
                out.append({'tid': f'cand:{r["name"]}:{i}', 'name': r['name'], 'pool': pool, 'prompt': r['prompt'],
                            'kind': 'cand', 'proof': p})
    wj(f'data/tj/cand_s{s}.jsonl', out)
    print(f'seed {s}: {len(out)} candidate proofs for {len({o["name"] for o in out})} solved theorems')


def select(s):
    C = {o['tid']: o for o in rj(f'data/tj/cand_s{s}.jsonl')}
    meta = {m['tid']: m for m in rj(f'artifacts/tj/score/cand_s{s}/targets.jsonl')}
    sc = {o['tid']: o for o in rj(f'artifacts/tj/score/cand_s{s}/s{s}_r8.jsonl')}
    best = {}
    for tid, o in sc.items():
        c = C[tid]
        key = (-o['T1.0']['total'], meta[tid]['n_steps'], c['proof'])
        if c['name'] not in best or key < best[c['name']][0]:
            best[c['name']] = (key, tid)
    nfail = sum(1 for m in meta.values() if not m['replay_ok'])
    unsc = sorted({C[t]['name'] for t in C} - set(best))
    ev = []
    for name, (key, tid) in sorted(best.items()):
        c = C[tid]
        ev.append({'tid': 'ev:' + name, 'name': name, 'pool': c['pool'], 'prompt': c['prompt'], 'kind': 'ev', 'proof': c['proof'],
                   'r8_logp': -key[0], 'n_cands': sum(1 for t in C if C[t]['name'] == name)})
    wj(f'data/tj/eventual_s{s}.jsonl', ev)
    wj(f'data/tj/targets_s{s}.jsonl', rj('data/tj/ref_targets.jsonl') + ev)
    print(f'seed {s}: eventual proofs for {len(ev)} theorems; candidate replay failures {nfail}; '
          f'solved theorems with no scorable candidate: {len(unsc)} {unsc[:10]}')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('what', choices=['refs', 'cands', 'select'])
    ap.add_argument('--seed', type=int)
    a = ap.parse_args()
    {'refs': lambda: refs(), 'cands': lambda: cands(a.seed), 'select': lambda: select(a.seed)}[a.what]()

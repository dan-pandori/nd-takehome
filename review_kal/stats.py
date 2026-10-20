#!/usr/bin/env python3
"""Dataset statistics of K12-Kalmár (sl, and the pb variant from my own builder) against K12's own proofs, all 155,000
theorems: ND lines, state-env pairs, pair tokens (state + action + eos), longest state / action, largest canonical name,
canonical lean_seq tokens.  States / actions from the project env (state_env.decompose, canonical names) -- the
trainer's input -- counted here.

  python3 review_kal/stats.py -> out/stats.json
"""
import collections, json, os, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kc
sys.path.insert(0, kc.ROOT)
from state_env import decompose

NAME = re.compile(r'^n(\d+)$')


def summ(x):
    x = sorted(x)
    return {'n': len(x), 'mean': round(sum(x) / len(x), 2), 'p50': x[len(x) // 2], 'p99': x[int(0.99 * len(x))], 'max': x[-1], 'sum': sum(x)}


acc = collections.defaultdict(list)
longest = {}
t0 = time.time()
for i, line in enumerate(kc.opener(os.path.join(kc.ROOT, 'data', 'kalmar', 'train_kal_sl.jsonl.gz'))):
    r = json.loads(line)
    for lab, proof in (('kal', r['proof']), ('k12', r['k12_proof'])):
        steps, toks, env = decompose(r['prompt'], proof, canon=True)
        acc[lab + '_lines'].append(proof.count(';'))
        acc[lab + '_pairs'].append(len(steps))
        pt = [len(s) + len(a) + 1 for s, a, h in steps]
        acc[lab + '_pair_tokens'].append(sum(pt))
        ms = max(len(s) for s, a, h in steps); ma = max(len(a) for s, a, h in steps)
        acc[lab + '_max_state'].append(ms); acc[lab + '_max_action'].append(ma)
        acc[lab + '_max_name'].append(max([int(m.group(1)) for t in toks if (m := NAME.match(t))] or [0]))
        acc[lab + '_lean_tokens'].append(len(toks))
        j = max(range(len(steps)), key=lambda q: pt[q])
        if pt[j] > longest.get(lab, (0,))[0]:
            longest[lab] = (pt[j], i, len(steps[j][0]), len(steps[j][1]))
    pb = kc.kalmar(r['prompt'], 'pb')
    acc['pb_lines'].append(pb['n_lines']); acc['pb_actions'].append(len(pb['acts']))
    if i % 20000 == 0:
        print(i, round(time.time() - t0), flush=True)
out = {k: summ(v) for k, v in acc.items()}
out['longest_pair'] = longest
print(json.dumps(out, indent=1))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', 'stats.json'), 'w'), indent=1)

#!/usr/bin/env python3
"""Build K12-Kalmár: one Kalmár proof (kalmar.py) per record of an ND record file, as an ND record, and check that it
decomposes and replays in the state environment (canonical names, arm SN).

  python3 kalmar/build.py --in data/kh/train_k12.jsonl --variant sl --out data/kalmar/train_kal_sl.jsonl \
      --stats artifacts/kalmar/build_sl.json [--procs 3] [--limit N]

Output records keep the input's fields (name, thm, key, prompt, ...) and replace `proof` / `n_lines` / `rules` with the
Kalmár proof's; they add `variant`, `n_actions`, `n_atoms`, `max_depth` (ND box depth), `tags` (one step type per
state-environment action, kalmar.TAGS), `k12_n_lines` (the input proof's length) and per-record shape numbers from the
decomposition: `max_state` / `max_action` (tokens, without <eos>), `pair_tokens` (sum over actions of state + action +
1), `max_name` (largest canonical name index), `env_depth` (largest frame depth), `lean_tokens` (length of the
canonical `lean_seq` text) and `term_size` (see kalmar.term_size).  A record that fails to decompose is written to
`<out>.fail.jsonl` and counted (the builder's tests require 0).
"""
import argparse, collections, json, os, sys, time
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kalmar
from state_env import decompose
from lean_tok import ParseFail

VARIANT = 'sl'


# lean_check's inference-node count per ND rule (run proof-strategies, `proof_strategies/strategies.py` WEIGHT: "IMPE
# NEGE ANDE ANDI ORI BOTE 1, IMPI NEGI 1 (+ body), ORE 3 (+ bodies), DN 3, R PR AS 0"; lean_check agreed on 400 / 400).
# Exact for proofs without dead lines, which these are: every line of a Kalmár proof is cited.
WEIGHT = {'IMPE': 1, 'NEGE': 1, 'ANDE1': 1, 'ANDE2': 1, 'ANDI': 1, 'ORI1': 1, 'ORI2': 1, 'BOTE': 1, 'IMPI': 1, 'NEGI': 1,
          'ORE': 3, 'DN': 3}


def term_size(nd_body):
    n = 0
    for ln in nd_body.split(' ; '):
        toks = ln.split()
        if ':' in toks:
            n += WEIGHT.get(toks[toks.index(':') + 1], 0)
    return n


def one(line):
    r = json.loads(line)
    try:
        b = kalmar.build(r['prompt'], VARIANT)
    except Exception as e:      # noqa: BLE001 -- any builder error is a failure to report, not to hide
        return None, {'name': r.get('name'), 'prompt': r['prompt'], 'why': f'build: {e!r}'}
    if b is None:
        return None, {'name': r.get('name'), 'prompt': r['prompt'], 'why': 'not valid (countermodel)'}
    try:
        steps, toks, env = decompose(r['prompt'], b['proof'], canon=True)
    except (ParseFail, ValueError, AssertionError, IndexError, KeyError) as e:
        return None, {'name': r.get('name'), 'prompt': r['prompt'], 'why': f'decompose: {e}'}
    if len(steps) != b['n_actions']:
        return None, {'name': r.get('name'), 'prompt': r['prompt'],
                      'why': f'tags {b["n_actions"]} != actions {len(steps)}'}
    ms = max(len(s) for s, a, h in steps)
    ma = max(len(a) for s, a, h in steps)
    pt = sum(len(s) + len(a) + 1 for s, a, h in steps)
    mn = max((int(t[1:]) for t in toks if t[:1] == 'n' and t[1:].isdigit()), default=0)
    out = dict(r)
    out['k12_n_lines'] = r.get('n_lines')
    out['k12_proof'] = r['proof']
    out.update(variant=VARIANT, proof=b['proof'], n_lines=b['n_lines'], n_actions=b['n_actions'],
               n_atoms=b['n_atoms'], max_depth=b['max_depth'], tags=b['tags'], max_state=ms, max_action=ma,
               pair_tokens=pt, max_name=mn, lean_tokens=len(toks), term_size=term_size(b['proof']),
               rules=sorted({ln.split(' : ')[1].split()[0] for ln in b['proof'][:-4].split(' ; ') if ' : ' in ln}))
    return out, None


def init(v):
    global VARIANT
    VARIANT = v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--variant', default='sl', choices=['sl', 'pb'])
    ap.add_argument('--out', required=True)
    ap.add_argument('--stats', default=None)
    ap.add_argument('--procs', type=int, default=3)
    ap.add_argument('--limit', type=int, default=0)
    a = ap.parse_args()
    lines = [l for l in open(a.inp) if l.strip()]
    if a.limit:
        lines = lines[:a.limit]
    t0 = time.time()
    nfail = 0
    agg = collections.defaultdict(list)
    with open(a.out, 'w') as fo, open(a.out + '.fail.jsonl', 'w') as ff, \
            Pool(a.procs, initializer=init, initargs=(a.variant,)) as pool:
        for out, fail in pool.imap(one, lines, chunksize=64):
            if fail:
                nfail += 1
                ff.write(json.dumps(fail) + '\n')
                continue
            fo.write(json.dumps(out) + '\n')
            for k in ('n_lines', 'n_actions', 'n_atoms', 'max_depth', 'max_state', 'max_action', 'pair_tokens',
                      'max_name', 'lean_tokens', 'term_size', 'k12_n_lines'):
                agg[k].append(out[k])
    st = {'in': a.inp, 'out': a.out, 'variant': a.variant, 'records': len(agg['n_lines']), 'failed': nfail,
          'secs': round(time.time() - t0, 1)}
    for k, xs in agg.items():
        xs = sorted(xs)
        st[k] = {'mean': sum(xs) / len(xs), 'max': xs[-1], 'p50': xs[len(xs) // 2], 'p99': xs[int(len(xs) * 0.99)],
                 'sum': sum(xs)}
    print(json.dumps(st, indent=1))
    if a.stats:
        json.dump(st, open(a.stats, 'w'), indent=1)


if __name__ == '__main__':
    main()

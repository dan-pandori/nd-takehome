#!/usr/bin/env python3
"""S_short's proofs: the shortest proof `minlen.Search` finds (bound 14 lines, 120 s per theorem), as in
`proof_strategies/search_proofs.py` on the fork branch dan_proof-strategies (its `work` and `trivial_proof`, unchanged
apart from the output fields).  minlen's internal nd_verify call is not used: the stream builder checks every proof's
literal canonical lean_seq text with Lean (`build_streams.py`), and only Lean-accepted proofs are kept.

  python3 style_edl/search_short.py --in data/kalmar/tf1200_kal_sl.jsonl --out data/style_edl/short/tf1200_minlen14.jsonl --procs 6
"""
import argparse, json, os, sys, time
from multiprocessing import Pool
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import minlen                                              # noqa: E402
from gen import fstr                                       # noqa: E402


def trivial_proof(prem, concl):
    toks = []
    for i, p in enumerate(prem):
        toks += [f'N{i + 1}', fstr(p), ':', 'PR', ';']
    if prem[-1] != concl:
        toks += [f'N{len(prem) + 1}', fstr(concl), ':', 'R', f'N{prem.index(concl) + 1}', ';']
    return ' '.join(toks + ['QED'])


def work(args):
    rec, bound, tl = args
    t0 = time.process_time()
    prem, concl = minlen.parse_thm(rec['prompt'])
    out = {'name': rec.get('name'), 'prompt': rec['prompt'], 'nd': None, 'n_lines': None, 'timeout': False}
    if concl in prem:
        out['nd'] = trivial_proof(prem, concl)
        out['n_lines'] = out['nd'].count(';')
    else:
        s = minlen.Search(prem, concl, deadline=time.time() + tl, lemmas=True)
        try:
            r = s.run(bound)
            if r:
                out['n_lines'], out['nd'] = r
        except minlen.Timeout:
            out['timeout'] = True
    out['secs'] = round(time.process_time() - t0, 3)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--bound', type=int, default=14)
    ap.add_argument('--time', type=float, default=120)
    ap.add_argument('--procs', type=int, default=2)
    a = ap.parse_args()
    recs = [json.loads(l) for l in open(a.inp) if l.strip()]
    t0 = time.time()
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    n = found = to = 0
    with Pool(a.procs) as pool, open(a.out + '.tmp', 'w') as f:
        for o in pool.imap(work, [(r, a.bound, a.time) for r in recs], chunksize=1):
            f.write(json.dumps(o) + '\n'); f.flush()
            n += 1; found += o['nd'] is not None; to += o['timeout']
    os.replace(a.out + '.tmp', a.out)
    print(json.dumps({'in': a.inp, 'n': n, 'found': found, 'timeouts': to, 'wall_s': round(time.time() - t0, 1),
                      'bound': a.bound, 'time': a.time}))


if __name__ == '__main__':
    main()

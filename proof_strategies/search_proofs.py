#!/usr/bin/env python3
"""Search proofs for theorems that have none (textbook-schema instances, textbook72) and for a K12 sample (a like-for-
like comparison with minimal textbook proofs).  Uses minlen.Search (bounded shortest-proof search in its restricted
formula space, iterative deepening on the line count) WITHOUT minlen's internal nd_verify call: every found proof is
checked by Lean (nd2lean.translate + Lean core) and only Lean-accepted proofs are kept (Lean alone decides).

  python3 proof_strategies/search_proofs.py --in SET.jsonl --out data/ps/search/SET.jsonl --bound 14 --time 120 --procs 2 \
      [--only_missing] [--sample 1000 --seed 0 --strata n_lines]

Output rows: {name, prompt, proof (or null), n_lines, secs, timeout, lean_ok, lean_msg}.  textbook72 rows are written
like any other but must never be printed (scoring only).
"""
import argparse, collections, gzip, json, os, random, sys, time
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
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
    out = {'name': rec.get('name'), 'prompt': rec['prompt'], 'proof': None, 'n_lines': None, 'timeout': False}
    if concl in prem:
        out['proof'] = trivial_proof(prem, concl)
        out['n_lines'] = out['proof'].count(';')
    else:
        s = minlen.Search(prem, concl, deadline=time.time() + tl, lemmas=True)
        try:
            r = s.run(bound)
            if r:
                out['n_lines'], out['proof'] = r
        except minlen.Timeout:
            out['timeout'] = True
    out['secs'] = round(time.process_time() - t0, 3)
    return out


def get_proof_field(r):
    for k in ('proof', 'gen_proof', 'reference_proof'):
        if r.get(k) not in (None, '', 'None'):
            return r[k]
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--bound', type=int, default=14)
    ap.add_argument('--time', type=float, default=120)
    ap.add_argument('--procs', type=int, default=2)
    ap.add_argument('--only_missing', action='store_true', help='only records without a proof')
    ap.add_argument('--sample', type=int, default=0)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--strata', default=None, help='field to stratify the sample by (equal share per value)')
    ap.add_argument('--no_lean', action='store_true', help='skip the Lean check (pods have no Lean; check on the VPS)')
    a = ap.parse_args()
    op = (lambda f: gzip.open(f, 'rt')) if a.inp.endswith('.gz') else open
    recs = []
    for i, line in enumerate(op(a.inp)):
        r = json.loads(line)
        r.setdefault('name', f'{os.path.basename(a.inp).split(".")[0]}_{i}')
        r['_i'] = i
        if a.only_missing and get_proof_field(r):
            continue
        recs.append(r)
    if a.sample:
        rng = random.Random(a.seed)
        if a.strata:
            groups = collections.defaultdict(list)
            for r in recs:
                groups[r[a.strata]].append(r)
            per = a.sample // len(groups)
            recs = [r for k in sorted(groups) for r in rng.sample(groups[k], min(per, len(groups[k])))]
        else:
            recs = rng.sample(recs, a.sample)
    t0 = time.time()
    with Pool(a.procs) as pool:
        res = list(pool.imap(work, [(r, a.bound, a.time) for r in recs], chunksize=1))
    for r, o in zip(recs, res):
        o['src_index'] = r['_i']
    wall = time.time() - t0
    if not a.no_lean:
        lean_rows(res)
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    with open(a.out, 'w') as f:
        for o in res:
            f.write(json.dumps(o) + '\n')
    n = len(res); found = sum(1 for o in res if o['proof']); ok = sum(1 for o in res if o.get('lean_ok'))
    print(json.dumps({'in': a.inp, 'n': n, 'found': found, 'lean_ok': ok, 'timeouts': sum(o['timeout'] for o in res),
                      'cpu_s': round(sum(o['secs'] for o in res), 1), 'wall_s': round(wall, 1), 'bound': a.bound, 'time': a.time}))


def lean_rows(res):
    """Lean decides: set lean_ok / lean_msg on every row with a proof."""
    from nd2lean import translate, lean_check, TranslationError
    idx, srcs = [], []
    for k, o in enumerate(res):
        if o['proof']:
            try:
                srcs.append(translate(o['prompt'], o['proof'])); idx.append(k)
            except TranslationError as e:
                o['lean_ok'], o['lean_msg'] = False, f'translation: {e}'
    for k, (ok, msg) in zip(idx, lean_check(srcs)):
        res[k]['lean_ok'], res[k]['lean_msg'] = ok, msg[:200]
    return res


if __name__ == '__main__':
    main()

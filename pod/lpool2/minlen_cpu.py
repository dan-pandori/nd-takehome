#!/usr/bin/env python3
"""minlen.py's search with (1) the time limit in the worker's CPU seconds instead of wall seconds and (2) one
subprocess per theorem (long-pool-2).

Same arguments and output lines as `minlen.py --in --out --bound --time --procs`; the search (`minlen.minlen`) is
unchanged.  (1): `minlen.time.time` is replaced by `time.process_time`, so the deadline and the recorded `secs` are CPU
seconds -- needed on hosts where a worker gets a fraction of a core (lp2-a: ~15 %).  (2): minlen.py's multiprocessing
pool hung on lp2-c when a worker process died (Pool.imap waits forever for the lost task) and hands out 4 theorems per
task; here a theorem whose process dies is written as {'min_lines_ub': None, 'timeout': False, 'error': 'worker died rc=..'}
(= unknown, excluded downstream) and the rest go on.
"""
import argparse, json, os, sys, time, types, subprocess
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


def one():
    import minlen
    minlen.time = types.SimpleNamespace(time=time.process_time, process_time=time.process_time, sleep=time.sleep)
    rec, bound, tl = json.loads(sys.stdin.read())
    t0 = time.process_time()
    r = minlen.minlen(rec['prompt'], bound, tl)
    r['secs'] = time.process_time() - t0
    print(json.dumps(r))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp'); ap.add_argument('--out'); ap.add_argument('--bound', type=int)
    ap.add_argument('--time', type=float); ap.add_argument('--procs', type=int, default=8)
    ap.add_argument('--one', action='store_true')
    a = ap.parse_args()
    if a.one:
        return one()
    recs = [json.loads(l) for l in open(a.inp) if l.strip()]

    def run(rec):
        p = subprocess.run([sys.executable, os.path.abspath(__file__), '--one'], input=json.dumps([rec, a.bound, a.time]),
                           capture_output=True, text=True)
        if p.returncode != 0 or not p.stdout.strip():
            return {'min_lines_ub': None, 'proof': None, 'timeout': False, 'bound': a.bound,
                    'error': f'worker died rc={p.returncode} {p.stderr[-300:]}'}
        return json.loads(p.stdout.strip().splitlines()[-1])

    t0 = time.time(); n_err = n_to = n_found = 0
    with ThreadPoolExecutor(a.procs) as ex, open(a.out, 'w') as fo:
        for i, (rec, r) in enumerate(zip(recs, ex.map(run, recs))):
            out = {k: rec[k] for k in ('name', 'thm', 'prompt') if k in rec}
            out['gen_lines'] = rec.get('n_lines', rec.get('gen_lines'))
            out.update(r)
            fo.write(json.dumps(out) + '\n'); fo.flush()
            n_err += 'error' in r; n_to += bool(r.get('timeout')); n_found += r['min_lines_ub'] is not None
            if (i + 1) % 200 == 0:
                print(f'{i+1}/{len(recs)} {time.time()-t0:.0f}s', flush=True)
    print(f'{len(recs)} theorems; labelled {n_found}; timeouts {n_to}; errors {n_err}')


if __name__ == '__main__':
    main()

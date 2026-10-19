#!/usr/bin/env python3
"""Check K12-Kalmár records with Lean, on the literal canonical `lean_seq` text the trainer sees (run kalmar-pretrain).

For every record: decompose (canonical names, as `state_train` does) -> the environment's rendered text; that text
must parse in the strict grammar (`lean_tok.inverse`) and denote the record's ND proof exactly; then Lean 4 core
checks `theorem t (P Q R S : Prop) (h1 : ...) : C := by <text>` (`lean_gate.check_sources`, the judge's Lean call).
Lean alone decides; `nd_verify` is not called.

  python3 kalmar/lean_check_kal.py --in data/kalmar/train_kal_sl.jsonl --out artifacts/kalmar/lean_check_sl.json \
      [--limit N] [--every K]
"""
import argparse, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from state_env import decompose
from lean_tok import LeanTokenizer, inverse, ParseFail
import lean_gate


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--every', type=int, default=1, help='check every K-th record')
    ap.add_argument('--fails', default=None, help='write failing records here (jsonl)')
    a = ap.parse_args()
    tok = LeanTokenizer('lean_staten')
    srcs, names, struct_bad = [], [], []
    t0 = time.time()
    n = 0
    for i, l in enumerate(open(a.inp)):
        if a.limit and n >= a.limit:
            break
        if i % a.every:
            continue
        r = json.loads(l)
        n += 1
        try:
            steps, toks, env = decompose(r['prompt'], r['proof'], canon=True)
            nd = inverse(toks)
            if nd.split() != r['proof'].split():
                struct_bad.append({'name': r.get('name'), 'why': 'inverse != record proof'})
                continue
        except ParseFail as e:
            struct_bad.append({'name': r.get('name'), 'why': f'parse: {e}'})
            continue
        srcs.append(f'{tok.statement(r["prompt"])} {tok.text(toks)}')
        names.append(r.get('name'))
    t1 = time.time()
    ok, wall, proc = lean_gate.check_sources(srcs)
    rej = [nm for nm, o in zip(names, ok) if not o]
    out = {'in': a.inp, 'checked': n, 'structural_failures': len(struct_bad), 'lean_checked': len(srcs),
           'lean_accepted': sum(ok), 'lean_rejected': len(rej), 'rejected_names': rej[:50],
           'structural_examples': struct_bad[:20], 'prep_s': round(t1 - t0, 1), 'lean_wall_s': round(wall, 1),
           'lean_proc_s': round(proc, 1), 'workers': lean_gate.WORKERS, 'every': a.every}
    print(json.dumps(out, indent=1))
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    json.dump(out, open(a.out, 'w'), indent=1)
    if a.fails and (rej or struct_bad):
        with open(a.fails, 'w') as f:
            for x in struct_bad:
                f.write(json.dumps(x) + '\n')
            for nm in rej:
                f.write(json.dumps({'name': nm, 'why': 'lean rejected'}) + '\n')


if __name__ == '__main__':
    main()

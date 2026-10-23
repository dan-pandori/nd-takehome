#!/usr/bin/env python3
"""S_own pilot (run `style-edl`, before the pre-registration; VPS CPU): the seed-0 learner's own greedy proofs only.

  python3 style_edl/pilot_own.py --out data/style_edl/pilot

Proofs: kalmar-pretrain's greedy read of the same checkpoint on tf1200 (`ctl_s0__tf1200_greedy.rows.jsonl.gz`,
bucket kalmar-pretrain/artifacts/kalmar/free/; stage1_best12_s0_b1200.pt, md5 9c436c35).  Pilot theorems (a proxy of
the final filter, which needs pass@32 reads): greedy valid and 8 / 8 of kalmar-pretrain's T 0.8 k 8 read valid
(`ctl_s0__tf1200_t08k8.rows.jsonl.gz`).  256 sampled (seed 7, not the final seed), split 128 / 128 by renaming class.
Writes stream / test jsonl files {name, prompt, nd, n_atoms} for edl_run.py.
"""
import argparse, collections, gzip, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import split as SP
from lean_tok import inverse
from tokenizer import make_tokenizer
from tf_agree import shift


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='data/style_edl/pilot')
    ap.add_argument('--seed', type=int, default=7)
    a = ap.parse_args()
    R = C.ROOT
    tok = make_tokenizer('lean_staten')
    tf = {json.loads(l)['name']: json.loads(l) for l in open(f'{R}/data/kalmar/tf1200_kal_sl.jsonl')}
    g = {}
    for l in gzip.open(f'{R}/data/style_edl/inherited/ctl_s0__tf1200_greedy.rows.jsonl.gz', 'rt'):
        r = json.loads(l); g[r['name']] = r
    k8 = collections.defaultdict(list)
    for l in gzip.open(f'{R}/data/style_edl/inherited/ctl_s0__tf1200_t08k8.rows.jsonl.gz', 'rt'):
        r = json.loads(l); k8[r['name']].append(r['valid'])
    elig, bad = [], collections.Counter()
    for nm, t in tf.items():
        r = g[nm]
        if not r['valid'] or sum(k8[nm]) < 8:
            bad['filter'] += 1; continue
        toks = SP.text_toks(r['text'], tok.stoi)
        nd = inverse(toks)
        steps, ctoks, env = C.decompose(t['prompt'], nd, canon=True)
        if shift(ctoks, r['base']) != toks:
            bad['canon_mismatch'] += 1; continue
        elig.append({'name': nm, 'prompt': t['prompt'], 'nd': nd, 'n_atoms': t['n_atoms']})
    st, te = SP.sample_and_split(elig, 256, a.seed)
    os.makedirs(a.out, exist_ok=True)
    for fn, rs in (('S_own.stream.jsonl', st), ('S_own.test.jsonl', te)):
        with open(os.path.join(a.out, fn), 'w') as f:
            for r in rs:
                f.write(json.dumps(r) + '\n')
    print(json.dumps({'eligible': len(elig), 'excluded': dict(bad), 'stream': len(st), 'test': len(te),
                      'atoms_stream': dict(sorted(collections.Counter(r['n_atoms'] for r in st).items())),
                      'atoms_test': dict(sorted(collections.Counter(r['n_atoms'] for r in te).items()))}))


if __name__ == '__main__':
    main()

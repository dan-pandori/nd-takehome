#!/usr/bin/env python3
"""V(x): every distinct Lean-valid proof of each of the 256 theorems that run `style-edl` collected (for l_V).

  python3 style_edl/build_vset.py --out data/style_edl/vset.jsonl

Sources (plain reads only, so stream and test theorems are treated alike): the six streams of the three seeds
(`data/style_edl/streams/`), the greedy reads of the bases and r8 (kal_free rows: `text` of valid attempts), and the
accepted texts of every plain guided_eval read in `artifacts/style_edl/reads/` and `artifacts/style_edl/cap/` (the
selection and S_own2 reads; the capability reads of the bases and of every theta*).  Every read's accepted text was
Lean-accepted by `lean_gate` in that read; stream proofs were Lean-checked by the builder.  Proofs are identified by
their canonical action sequence (`common.canon_key`).  Output rows {name, prompt, nd, sources: [file tags]}.
"""
import argparse, collections, glob, gzip, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import split as SP
from lean_tok import inverse
from tokenizer import make_tokenizer


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--streams', default='data/style_edl/streams')
    ap.add_argument('--reads', default='artifacts/style_edl/reads,artifacts/style_edl/cap')
    ap.add_argument('--out', default='data/style_edl/vset.jsonl')
    a = ap.parse_args()
    R = C.ROOT
    tok = make_tokenizer('lean_staten')
    man = json.load(open(f'{R}/style_edl/streams_manifest.json'))
    names = set(man['theorems']['stream']) | set(man['theorems']['test'])
    prompt = {}
    V = collections.defaultdict(dict)            # name -> canon key -> {'nd', 'sources'}
    bad = collections.Counter()

    def add(nm, nd, tag):
        try:
            k = C.canon_key(prompt[nm], nd)
        except Exception:
            bad[tag] += 1
            return
        e = V[nm].setdefault(k, {'nd': nd, 'sources': []})
        if tag not in e['sources']:
            e['sources'].append(tag)

    for fn in sorted(glob.glob(f'{R}/{a.streams}/s*/*.jsonl')):
        tag = os.path.relpath(fn, f'{R}/{a.streams}').replace('.jsonl', '')
        for l in open(fn):
            r = json.loads(l)
            prompt[r['name']] = r['prompt']
            add(r['name'], r['nd'], tag)
    for d in a.reads.split(','):
        for fn in sorted(glob.glob(f'{R}/{d}/*.rows.jsonl.gz')):
            if '_logical_' in fn:
                continue                          # guided reads: test theorems only, kept out of V
            tag = os.path.basename(fn).replace('.rows.jsonl.gz', '')
            for l in gzip.open(fn, 'rt'):
                r = json.loads(l)
                nm = r.get('name')
                if nm not in names:
                    continue
                texts = list(r['accepted']) if 'accepted' in r else ([r['text']] if r.get('valid') else [])
                for t in texts:
                    try:
                        nd = inverse(SP.text_toks(t, tok.stoi))
                    except Exception:
                        bad[tag] += 1
                        continue
                    add(nm, nd, tag)
    os.makedirs(os.path.dirname(f'{R}/{a.out}'), exist_ok=True)
    n = 0
    with open(f'{R}/{a.out}', 'w') as f:
        for nm in sorted(V):
            for k, e in V[nm].items():
                f.write(json.dumps({'name': nm, 'prompt': prompt[nm], 'nd': e['nd'], 'sources': e['sources']}) + '\n')
                n += 1
    sizes = sorted(len(V[nm]) for nm in V)
    print(json.dumps({'theorems': len(V), 'proofs': n, 'median_size': sizes[len(sizes) // 2], 'max_size': sizes[-1],
                      'unparsed': dict(bad)}))


if __name__ == '__main__':
    main()

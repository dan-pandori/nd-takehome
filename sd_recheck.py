#!/usr/bin/env python3
"""Checker of record for this run's counted proofs, by an INDEPENDENT route, with no GPU.

`sd_eval.py` counts a sample iff its literal sampled Lean text parses in the strict `lean_seq`
grammar and Lean accepts that literal text.  This script takes a random sample of the stored
proofs, decodes each literal text back to the ND proof it denotes (`lean_tok.inverse`), and asks
run `lean-judge`'s `lean_judge.verify_text` -- which re-translates that ND proof through
`nd2lean.translate` and checks the *translation* in Lean.  Two different Lean sources for the same
proof: agreement means nothing counted here depends on which rendering was checked.

  python3 sd_recheck.py [--n 400] [--seed 0] --out artifacts/sd/recheck.json
"""
import argparse, glob, json, os, random, sys, time, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lean_tok import LeanTokenizer, inverse, ParseFail
import lean_judge

ap = argparse.ArgumentParser()
ap.add_argument('--n', type=int, default=400)
ap.add_argument('--seed', type=int, default=0)
ap.add_argument('--heldout', default='data/p2/heldout.jsonl')
ap.add_argument('--ev', default='artifacts/sd/ev')
ap.add_argument('--out', default='artifacts/sd/recheck.json')
a = ap.parse_args()

prompts = {}
for l in open(a.heldout):
    r = json.loads(l)
    prompts[r['name']] = r['prompt']

tok = LeanTokenizer('lean_seq')


def retok(text):
    """the literal text back into grammar tokens: text() glues .1 .2 .elim onto the preceding name.
    `Or.elim` is itself one vocabulary token, so a word that is already in the vocabulary is never
    split -- getting this wrong rejects exactly the ORE proofs (~1.4 % of the pool)."""
    out = []
    for w in text.split():
        if w in tok.stoi:
            out.append(w); continue
        for suf in ('.elim', '.1', '.2'):
            if w.endswith(suf) and w != suf:
                out.append(w[:-len(suf)]); out.append(suf); break
        else:
            out.append(w)
    return out


# only the files that carry the literal text (the --texts evaluations: every arm's final checkpoint)
files = [f for f in sorted(glob.glob(os.path.join(a.ev, '*.jsonl')))
         if '.step' not in os.path.basename(f) and not f.endswith('.gz')]
pool = []
for fn in files:
    stem = os.path.basename(fn)[:-6]
    for l in open(fn):
        r = json.loads(l)
        if r.get('lean_ok') and r.get('text'):
            pool.append((stem, r['name'], r['text']))
rng = random.Random(a.seed)
pick = rng.sample(pool, min(a.n, len(pool)))

pairs, meta, bad_parse = [], [], []
for stem, name, text in pick:
    try:
        nd = inverse(retok(text))
    except ParseFail as e:
        bad_parse.append({'stem': stem, 'name': name, 'reason': str(e)})
        continue
    pairs.append((prompts[name], nd))
    meta.append({'stem': stem, 'name': name})

t0 = time.time()
res = lean_judge.judge_many(pairs)
wall = time.time() - t0
agree = sum(1 for ok, _, _ in res if ok)
dis = [dict(m, reason=rs) for m, (ok, rs, _) in zip(meta, res) if not ok]
per_arm = collections.Counter(m['stem'].split('_s')[0] for m in meta)
out = {'utc': time.strftime('%FT%TZ', time.gmtime()),
       'route_a': 'sd_eval.py: Lean on the literal sampled lean_seq text (what this run counted)',
       'route_b': 'lean_judge.verify_text: the denoted ND proof re-translated by nd2lean and checked in Lean',
       'files_with_texts': len(files), 'accepted_proofs_available': len(pool),
       'sampled': len(pick), 'grammar_reparse_failures': len(bad_parse),
       'checked': len(pairs), 'route_b_accepts': agree,
       'agreement': agree / max(len(pairs), 1), 'disagreements': dis[:20],
       'per_checkpoint_counts': dict(sorted(per_arm.items())),
       'lean_wall_s': wall, 'lean_judge_stats': lean_judge.stats()}
json.dump(out, open(a.out, 'w'), indent=1)
print(json.dumps({k: v for k, v in out.items() if k not in ('disagreements', 'per_checkpoint_counts')}, indent=1))
if dis:
    print('first disagreements:', json.dumps(dis[:5], indent=1)[:900])

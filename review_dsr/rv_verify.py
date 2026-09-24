"""Reviewer's independent re-verification of counted proofs.

For each arm: sample N counted proofs across every counting stage, then
  (a) re-run nd_verify on the denoted ND proof,
  (b) translate with the unmodified nd2lean.py and check in Lean (the checker of record),
  (c) check the LITERAL sampled Lean text in Lean, using the arm's own statement header,
and report agreement.  Also re-derives line counts and term sizes.
"""
import sys, os, json, glob, re, random, collections
sys.path.insert(0, '/home/dan/work/ds-rendering')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nd_verify import verify_text
import nd2lean
from lean_tok import LeanTokenizer
import lean_gate
from rv_norm import nd_len, box_depth, term_size

N = int(sys.argv[1]) if len(sys.argv) > 1 else 250
MODE = {'c0': 'lean_seq', 'r1': 'lean_seq_noprem', 'r3': 'lean_seq_nofml',
        'r2': 'lean_seq_intro', 'r4': 'lean_seq_funbare'}
ROOT = '/home/dan/review/ds-rendering'


def counted(arm):
    """every counted proof of this arm, as (stage, prompt, nd proof, literal lean text)"""
    out = []
    d = os.path.join(ROOT, 'artifacts/dsr/dsr-%s' % arm)
    for fn in sorted(glob.glob(d + '/held_*.jsonl') + glob.glob(d + '/mech_*.jsonl')):
        st = 'held' if 'held_' in fn else 'mech'
        for l in open(fn):
            r = json.loads(l)
            for i, p in enumerate(r.get('proofs', [])):
                tx = r['lean_texts'][i] if i < len(r.get('lean_texts') or []) else None
                out.append((st, r['prompt'], p, tx))
    for fn in sorted(glob.glob(d + '/cov_*.s0.jsonl')):
        for l in open(fn):
            r = json.loads(l)
            for p in r.get('proofs', []):
                out.append(('cov', r['prompt'], p['proof'], p.get('text')))
    for sub in sorted(glob.glob(d + '/ei_d3_*_s?') + glob.glob(d + '/frz_d3_*_s?') + glob.glob(d + '/la_T1_*_s?')):
        st = os.path.basename(sub).split('_')[0]
        fs = glob.glob(sub + '/found_*.jsonl')
        if not fs:
            continue
        last = max(fs, key=lambda f: int(re.search(r'_(\d+)\.jsonl', f).group(1)))
        for l in open(last):
            r = json.loads(l)
            out.append((st, r['prompt'], r['proof'], r.get('text')))
    return out


summary = {}
for arm in ['c0', 'r1', 'r2', 'r3', 'r4']:
    pool = counted(arm)
    rng = random.Random(20260924)
    samp = rng.sample(pool, min(N, len(pool)))
    tok = LeanTokenizer(MODE[arm])
    nd_ok, srcs, bad_tr = [], [], 0
    for st, pr, nd, tx in samp:
        ok, reason, _nl = verify_text(pr + " " + nd)
        nd_ok.append(bool(ok))
        try:
            srcs.append(nd2lean.translate(pr, nd))
        except Exception as e:
            srcs.append(None); bad_tr += 1
    lean_res = nd2lean.lean_check([s for s in srcs if s is not None])
    it = iter(lean_res)
    lean_ok = [next(it)[0] if s is not None else False for s in srcs]
    # (c) literal sampled text
    lit = [(i, tok.statement(pr), tx) for i, (st, pr, nd, tx) in enumerate(samp) if tx]
    lok, _, _ = lean_gate.lean_check([(s, t) for _, s, t in lit])
    litmap = dict(zip([i for i, _, _ in lit], lok))
    bystage = collections.Counter(st for st, _, _, _ in samp)
    rec = dict(arm=arm, mode=MODE[arm], pool=len(pool), n=len(samp), stages=dict(bystage),
               nd_ok=sum(nd_ok), translate_fail=bad_tr, lean_ok=sum(lean_ok),
               agree=sum(a == b for a, b in zip(nd_ok, lean_ok)),
               nd_only=sum(a and not b for a, b in zip(nd_ok, lean_ok)),
               lean_only=sum(b and not a for a, b in zip(nd_ok, lean_ok)),
               literal_n=len(lit), literal_ok=sum(litmap.values()), literal_missing=len(samp) - len(lit),
               mean_nd_lines=sum(nd_len(nd) for _, _, nd, _ in samp) / len(samp),
               mean_term_tokens=sum(term_size(tx) for _, _, _, tx in samp if tx) / max(1, len(lit)),
               max_box_depth=max(box_depth(nd) for _, _, nd, _ in samp))
    summary[arm] = rec
    print(json.dumps(rec), flush=True)
    for i, (st, pr, nd, tx) in enumerate(samp):
        if not nd_ok[i] or not lean_ok[i] or (tx and not litmap.get(i, True)):
            print('  DISAGREE', arm, st, 'nd', nd_ok[i], 'lean', lean_ok[i], 'literal', litmap.get(i))
            print('   ', pr); print('   ', nd)
json.dump(summary, open(os.path.join(ROOT, 'rv/rv_verify.json'), 'w'), indent=1)

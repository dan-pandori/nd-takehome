#!/usr/bin/env python3
"""Theorem pool, the 128 / 128 split and the six streams per learner seed (run `style-edl`).

  python3 style_edl/build_streams.py --reads artifacts/style_edl/reads --short data/style_edl/short/tf1200_minlen14.jsonl \
      --out data/style_edl/streams [--seed 20261023]

Inputs (all from this run's reads, `pod/sedl/q1_reads.sh`):
  base_s{s}__tf1200_greedy.rows.jsonl.gz      kal_free.py greedy read of stage1_best12_s{s}_b1200 (S_own; S_seed of s-1)
  r8_s{s}__tf1200_greedy.rows.jsonl.gz        kal_free.py greedy read of la_T1_best12_s{s}_r8 (S_RL)
  base_s{s}__tf1200_plain_k32_seed1.rows.jsonl.gz   guided_eval.py plain, k 32, T 0.8, seed 1 (the selection read)
  base_s{s}__tf1200_plain_k4_seed3.rows.jsonl.gz    guided_eval.py plain, k 4, T 0.8, seed 3 (S_own2: first accepted)
  tf1200_minlen14.jsonl                       search_short.py (S_short)
  data/kalmar/tf1200_kal_sl.jsonl             the theorems and their Kalmár sl proofs (S_Kalmar)
A theorem is eligible iff, for every learner seed s: >= 29 / 32 of the selection read Lean-valid, the base's greedy
proof and r8's greedy proof Lean-valid, the k 4 draw has a Lean-valid attempt; and the minlen proof exists; and every
stream proof replays in the environment and its literal canonical lean_seq text is accepted by Lean (re-checked here,
`lean_gate.gate`).  256 eligible theorems are sampled (--seed) and split by renaming class (`split.sample_and_split`).
Outputs: streams/s{s}/{stream}.{stream,test}.jsonl ({name, prompt, nd, n_atoms, source}), pool.json (eligibility
counts, atom mix), streams_manifest.json (theorem ids, split, sources, sha256 of every proof and file).
"""
import argparse, collections, gzip, hashlib, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import split as SP
from lean_tok import inverse
from tokenizer import make_tokenizer
from tf_agree import shift

STREAMS = ('S_own', 'S_own2', 'S_seed', 'S_short', 'S_RL', 'S_Kal')
SEEDS = (0, 1, 2)
SEL_MIN = 29          # >= 29 / 32 = 0.906 >= 0.9


def rows(fn):
    return {r['name']: r for r in (json.loads(l) for l in gzip.open(fn, 'rt'))}


def text_nd(prompt, text, tok, base=None):
    """literal sampled text -> ND; checks that it replays and (if base given) that it is the canonical text shifted."""
    toks = SP.text_toks(text, tok.stoi)
    nd = inverse(toks)
    steps, ctoks, env = C.decompose(prompt, nd, canon=True)
    if base is not None and shift(ctoks, base) != toks:
        raise ValueError('not the canonical text')
    return nd


def sha(s):
    return hashlib.sha256(s.encode()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--reads', default='artifacts/style_edl/reads')
    ap.add_argument('--short', default='data/style_edl/short/tf1200_minlen14.jsonl')
    ap.add_argument('--tf', default='data/kalmar/tf1200_kal_sl.jsonl')
    ap.add_argument('--out', default='data/style_edl/streams')
    ap.add_argument('--n', type=int, default=256)
    ap.add_argument('--seed', type=int, default=20261023)
    a = ap.parse_args()
    tok = make_tokenizer('lean_staten')
    tf = [json.loads(l) for l in open(os.path.join(C.ROOT, a.tf))]
    R = os.path.join(C.ROOT, a.reads)
    g = {s: rows(f'{R}/base_s{s}__tf1200_greedy.rows.jsonl.gz') for s in SEEDS}
    r8 = {s: rows(f'{R}/r8_s{s}__tf1200_greedy.rows.jsonl.gz') for s in SEEDS}
    k32 = {s: rows(f'{R}/base_s{s}__tf1200_plain_k32_seed1.rows.jsonl.gz') for s in SEEDS}
    k4 = {s: rows(f'{R}/base_s{s}__tf1200_plain_k4_seed3.rows.jsonl.gz') for s in SEEDS}
    short = {r['name']: r for r in (json.loads(l) for l in open(os.path.join(C.ROOT, a.short)))}
    why = collections.Counter()
    cand = []
    for t in tf:
        nm, pr = t['name'], t['prompt']
        fail = []
        for s in SEEDS:
            if k32[s][nm]['n_ok'] < SEL_MIN: fail.append(f'sel_s{s}')
            if not g[s][nm]['valid']: fail.append(f'greedy_s{s}')
            if not r8[s][nm]['valid']: fail.append(f'r8_s{s}')
            if not k4[s][nm]['accepted']: fail.append(f'own2_s{s}')
        if short.get(nm, {}).get('nd') is None: fail.append('short_none')
        for f in fail:
            why[f] += 1
        if fail:
            why['excluded'] += 1
            continue
        try:
            p = {'S_Kal': t['proof'], 'S_short': short[nm]['nd']}
            for s in SEEDS:
                p[f'own_s{s}'] = text_nd(pr, g[s][nm]['text'], tok, g[s][nm]['base'])
                p[f'rl_s{s}'] = text_nd(pr, r8[s][nm]['text'], tok, r8[s][nm]['base'])
                p[f'own2_s{s}'] = text_nd(pr, next(iter(k4[s][nm]['accepted'])), tok)
            C.decompose(pr, p['S_Kal'], canon=True); C.decompose(pr, p['S_short'], canon=True)
        except Exception as e:                                   # ParseFail / ValueError
            why['replay_fail'] += 1; why['excluded'] += 1
            continue
        cand.append({'name': nm, 'prompt': pr, 'n_atoms': t['n_atoms'], 'p': p})
    # Lean on the literal canonical text (base 0) of every distinct candidate proof
    from lean_gate import gate
    items = sorted({(c['prompt'], nd) for c in cand for nd in c['p'].values()})
    texts = [tok.text(C.decompose(pr, nd, canon=True)[1]) for pr, nd in items]
    res = gate(tok, [pr for pr, _ in items], [nd for _, nd in items], texts)
    ok = {k: not r.startswith('LEAN') for k, r in zip(items, res)}
    elig = []
    for c in cand:
        bad = [k for k, nd in c['p'].items() if not ok[(c['prompt'], nd)]]
        for k in bad:
            why[f'lean_rej_{k}'] += 1
        if bad:
            why['excluded'] += 1
        else:
            elig.append(c)
    st, te = SP.sample_and_split(elig, a.n, a.seed)
    out = os.path.join(C.ROOT, a.out)
    man = {'seed': a.seed, 'n_eligible': len(elig), 'excluded': dict(why), 'lean_checked': len(items),
           'lean_rejected': sum(not v for v in ok.values()),
           'atoms_eligible': dict(sorted(collections.Counter(c['n_atoms'] for c in elig).items())),
           'atoms_stream': dict(sorted(collections.Counter(c['n_atoms'] for c in st).items())),
           'atoms_test': dict(sorted(collections.Counter(c['n_atoms'] for c in te).items())),
           'theorems': {'stream': [c['name'] for c in st], 'test': [c['name'] for c in te]},
           'pkey': {c['name']: repr(SP.pkey_of(c['prompt'])) for c in st + te},
           'files': {}, 'proof_sha256': {}}
    src = {'S_own': lambda s: (f'own_s{s}', f'base_s{s}__tf1200_greedy'),
           'S_own2': lambda s: (f'own2_s{s}', f'base_s{s}__tf1200_plain_k4_seed3 (first accepted)'),
           'S_seed': lambda s: (f'own_s{(s + 1) % 3}', f'base_s{(s + 1) % 3}__tf1200_greedy'),
           'S_short': lambda s: ('S_short', 'tf1200_minlen14 (minlen.Search bound 14, 120 s)'),
           'S_RL': lambda s: (f'rl_s{s}', f'r8_s{s}__tf1200_greedy (la_T1_best12_s{s}_r8)'),
           'S_Kal': lambda s: ('S_Kal', 'tf1200_kal_sl.jsonl proof (K12-Kalmar sl)')}
    for s in SEEDS:
        os.makedirs(f'{out}/s{s}', exist_ok=True)
        for S in STREAMS:
            key, desc = src[S](s)
            for part, cs in (('stream', st), ('test', te)):
                fn = f'{out}/s{s}/{S}.{part}.jsonl'
                with open(fn, 'w') as f:
                    for c in cs:
                        f.write(json.dumps({'name': c['name'], 'prompt': c['prompt'], 'nd': c['p'][key],
                                            'n_atoms': c['n_atoms'], 'source': desc}) + '\n')
                man['files'][os.path.relpath(fn, C.ROOT)] = sha(open(fn).read())
            man['proof_sha256'][f's{s}/{S}'] = {c['name']: sha(c['p'][key]) for c in st + te}
    # stream statistics: identity with the learner's own greedy proof, mean actions
    stats = {}
    for s in SEEDS:
        for S in STREAMS:
            key, _ = src[S](s)
            cs = st + te
            same = sum(C.canon_key(c['prompt'], c['p'][key]) == C.canon_key(c['prompt'], c['p'][f'own_s{s}']) for c in cs)
            acts = [len(C.decompose(c['prompt'], c['p'][key], canon=True)[0]) for c in cs]
            stats[f's{s}/{S}'] = {'identical_to_own_greedy': same / len(cs), 'mean_actions': sum(acts) / len(acts)}
    man['stream_stats'] = stats
    json.dump(man, open(os.path.join(C.ROOT, 'style_edl/streams_manifest.json'), 'w'), indent=1)
    print(json.dumps({k: man[k] for k in ('n_eligible', 'excluded', 'lean_checked', 'lean_rejected', 'atoms_eligible',
                                          'atoms_stream', 'atoms_test')}))
    for k, v in stats.items():
        print(k, json.dumps(v))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Reviewer recount of the hand-golfed Python programs (run kalmar-complexity).

  ~/review/kalmar-complexity/.venv-tok/bin/python rv_python.py sizes      # own size counts (needs `tokenizers`)
  python3 rv_python.py test --n 1000 --seed 271828                       # programs vs the builders, fresh sample
  python3 rv_python.py lean --n 150 --seed 314159                         # Lean on the programs' own outputs

sizes: raw UTF-8 bytes; raw DEFLATE (zlib 9, wbits -15); gzip -9 (with header, for reference); raw LZMA2 (preset 9e);
Qwen3 (Qwen/Qwen3-8B tokenizer.json, md5-checked against the hub) and GPT-2 token counts.
"""
import json, lzma, os, random, sys, time, zlib, gzip, io
HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.expanduser('~/review/kalmar-complexity')
PY = os.path.join(WS, 'kalmar_complexity', 'programs', 'python')
sys.path.insert(0, WS); sys.path.insert(0, os.path.join(WS, 'kalmar')); sys.path.insert(0, os.path.join(WS, 'kalmar_complexity', 'ref'))

PROGS = {
    'K-sl algorithm': ['ksl_alg.py'], 'K-sl render ND': ['ksl_nd.py'], 'K-sl render lean_seq': ['ksl_seq.py'],
    'parse': ['parse.py'], 'K-sl alg + lean_seq render': ['ksl_alg.py', 'ksl_seq.py'],
    'K-sl alg + ND render': ['ksl_alg.py', 'ksl_nd.py'],
    'K-tt algorithm': ['ktt_alg.py'], 'K-tt render Lean': ['ktt_lean.py'], 'K-tt alg + Lean render': ['ktt_alg.py', 'ktt_lean.py'],
    'K-sl per-step policy kpol': ['kpol.py'],
}
for c in ['copy', 'reverse', 'parity', 'parity_nb', 'sort', 'sort_nb', 'add', 'add_nb', 'eval', 'taut']:
    PROGS['calib ' + c] = ['calib/%s.py' % c]


def sizes():
    from tokenizers import Tokenizer
    q = Tokenizer.from_file(os.path.join(WS, 'kalmar_complexity/tok/qwen3/tokenizer.json'))
    g = Tokenizer.from_file(os.path.join(WS, 'kalmar_complexity/tok/gpt2/tokenizer.json'))
    out = {}
    for name, fs in PROGS.items():
        src = ''.join(open(os.path.join(PY, f), encoding='utf-8').read() for f in fs)
        b = src.encode('utf-8')
        c = zlib.compressobj(9, zlib.DEFLATED, -15); d = c.compress(b) + c.flush()
        bio = io.BytesIO()
        with gzip.GzipFile(fileobj=bio, mode='wb', compresslevel=9, mtime=0) as fh:
            fh.write(b)
        x = lzma.compress(b, format=lzma.FORMAT_RAW, filters=[{'id': lzma.FILTER_LZMA2, 'preset': 9 | lzma.PRESET_EXTREME}])
        out[name] = {'raw': len(b), 'deflate': len(d), 'gzip9': len(bio.getvalue()), 'xz_raw': len(x),
                     'qwen3': len(q.encode(src).ids), 'gpt2': len(g.encode(src).ids), 'trailing_newline': src.endswith('\n')}
    os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, 'out', 'python_sizes.json'), 'w'), indent=1)
    print(f"{'program':32} {'raw':>6} {'defl':>6} {'gz9':>6} {'xz':>6} {'qwen3':>6} {'gpt2':>6}")
    for k, v in out.items():
        print(f"{k:32} {v['raw']:6} {v['deflate']:6} {v['gzip9']:6} {v['xz_raw']:6} {v['qwen3']:6} {v['gpt2']:6}")


def sample(n, seed):
    ps = [json.loads(l)['prompt'] for l in open(os.path.join(WS, 'data/kh/train_k12.jsonl'))]
    return [ps[i] for i in sorted(random.Random(seed).sample(range(len(ps)), n))]


def progs():
    sys.path.insert(0, PY)
    from ksl_alg import K
    from ksl_nd import R
    from ksl_seq import Q
    from ktt_alg import T
    from ktt_lean import L
    from parse import S
    from kpol import A
    return K, R, Q, T, L, S, A


def test(n, seed):
    import kalmar, tt_prover
    from state_env import canonicalise, decompose
    K, R, Q, T, L, S, A = progs()
    ok = {'ksl_nd': 0, 'ksl_seq': 0, 'ktt_lean': 0, 'kpol_states': 0, 'kpol_exact': 0, 'neg_ksl_vs_pb': 0}
    per_tag_fail = {}
    t0 = time.time()
    for p in sample(n, seed):
        P, G = S(p)
        ref = kalmar.build(p, 'sl')
        ok['ksl_nd'] += R(K(P, G)) == ref['proof']
        ok['ksl_seq'] += Q(K(P, G)) == ' '.join(canonicalise(p, ref['proof']))
        ok['ktt_lean'] += L(T(P, G), P, G) == tt_prover.solve(p)
        ok['neg_ksl_vs_pb'] += R(K(P, G)) == kalmar.build(p, 'pb')['proof']
        steps, toks, env = decompose(p, ref['proof'], canon=True)
        assert len(steps) == len(ref['tags'])
        for (stt, act, _h), tag in zip(steps, ref['tags']):
            ok['kpol_states'] += 1
            good = ' '.join(A(list(stt))).split() == list(act)     # A returns formula strings as single items
            ok['kpol_exact'] += good
            if not good:
                per_tag_fail[tag] = per_tag_fail.get(tag, 0) + 1
    res = {'n': n, 'seed': seed, 'ok': ok, 'kpol_fail_by_tag': per_tag_fail, 'seconds': time.time() - t0}
    json.dump(res, open(os.path.join(HERE, 'out', f'python_test_s{seed}.json'), 'w'), indent=1)
    print(res)


# ---------------------------------------------------------------- Lean on the programs' outputs
def lean_formula(f):
    if f == 'F':
        return 'False'
    if isinstance(f, str):
        return f
    if f[0] == '~':
        return '(¬ %s)' % lean_formula(f[1])
    return '(%s %s %s)' % (lean_formula(f[1]), {'&': '∧', 'v': '∨', '>': '→'}[f[0]], lean_formula(f[2]))


def lean(n, seed):
    """K-tt: the Lean source the golfed program prints (a whole theorem).  K-sl: the golfed program's lean_seq text,
    wrapped as `theorem tK (P Q R S : Prop) (h1 : ..) .. : goal := by <text>`.  Each theorem gets a unique name;
    chunks of 25 with an `example : True := trivial` sentinel after each theorem; disagreements re-checked alone.
    Negative controls: one corrupted proof per chunk (a cited name swapped), which Lean must reject."""
    import subprocess, tempfile, re
    K, R, Q, T, L, S, A = progs()
    items = []
    for j, p in enumerate(sample(n, seed)):
        P, G = S(p)
        tt = L(T(P, G), P, G).replace('theorem t ', 'theorem tt%d ' % j, 1)
        hyps = ''.join(' (h%d : %s)' % (i + 1, lean_formula(x)) for i, x in enumerate(P))
        out_t = []
        for tk in Q(K(P, G)).split():                 # lean_seq -> Lean source: .1 / .2 / .elim attach to the name
            if tk in ('.1', '.2', '.elim') and out_t:
                out_t[-1] += tk
            else:
                out_t.append(tk)
        seq = 'theorem sl%d (P Q R S : Prop)%s : %s := by %s' % (j, hyps, lean_formula(G), ' '.join(out_t))
        items.append(('tt', j, tt)); items.append(('sl', j, seq))
    # negative controls: swap the last cited premise/hypothesis name in the final exact / a have
    negs = []
    for kind, j, src in items[:20]:
        bad = src.replace('Or.inl', 'Or.inr', 1) if 'Or.inl' in src else src.replace('.1', '.2', 1)
        bad = bad.replace('theorem tt%d ' % j, 'theorem ntt%d ' % j).replace('theorem sl%d ' % j, 'theorem nsl%d ' % j)
        if bad != src:
            negs.append(('neg_' + kind, j, bad))
    allitems = items + negs
    def run(chunk):
        body = 'set_option maxRecDepth 4000\n\n' + '\n\n'.join(src + '\n\nexample : True := trivial' for _, _, src in chunk)
        with tempfile.NamedTemporaryFile('w', suffix='.lean', delete=False, dir='/tmp') as fh:
            fh.write(body + '\n')
        out = subprocess.run([os.path.expanduser('~/.elan/bin/lean'), fh.name], capture_output=True, text=True)
        os.unlink(fh.name)
        return out.returncode, out.stdout + out.stderr
    verdict = {}
    for c0 in range(0, len(allitems), 25):
        chunk = allitems[c0:c0 + 25]
        rc, msg = run(chunk)
        bad_names = set(re.findall(r"(?:error|warning)[^\n]*?\b((?:n?tt|n?sl)\d+)\b", msg))
        has_err = 'error' in msg
        for kind, j, src in chunk:
            nm = re.match(r'theorem (\S+)', src).group(1)
            verdict[(kind, j)] = None if has_err else True
        if has_err or 'sorry' in msg:
            for kind, j, src in chunk:      # re-check one by one
                rc1, m1 = run([(kind, j, src)])
                verdict[(kind, j)] = ('error' not in m1 and 'sorry' not in m1 and rc1 == 0)
    summ = {}
    for (kind, j), v in verdict.items():
        summ.setdefault(kind, [0, 0]); summ[kind][0] += 1; summ[kind][1] += bool(v)
    scan = {'sorry_admit_auto': sum(any(w in src for w in ('sorry', 'admit', 'exact?', 'decide', 'simp', 'tauto', 'aesop'))
                                    for _, _, src in items)}
    res = {'n_theorems': n, 'seed': seed, 'checked_accepted': summ, 'scan': scan,
           'example_tt': items[0][2][:300], 'example_sl': items[1][2][:300]}
    json.dump(res, open(os.path.join(HERE, 'out', f'python_lean_s{seed}.json'), 'w'), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('what')
    ap.add_argument('--n', type=int, default=1000)
    ap.add_argument('--seed', type=int, default=271828)
    a = ap.parse_args()
    os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
    {'sizes': lambda: sizes(), 'test': lambda: test(a.n, a.seed), 'lean': lambda: lean(a.n, a.seed)}[a.what]()

#!/usr/bin/env python3
"""Sizes of the Python programs (run kalmar-complexity).  Run with the tokenizer venv:

  .venv-tok/bin/python kalmar_complexity/programs/python/measure.py   # -> artifacts/kc/python_sizes.json

Per program (a file, or a concatenation of files = a combined program): raw UTF-8 bytes; raw DEFLATE (zlib level 9,
no header); raw LZMA2 (xz preset 9e, FORMAT_RAW, no container); tokens of Qwen3 (`Qwen/Qwen3-8B` tokenizer.json) and
GPT-2 BPE.  Bits = 8 x bytes.  `mech:` rows are mechanical minifications (python-minifier: docstrings removed, locals
renamed) of whole reference files -- upper bounds that include unused code.
"""
import json, lzma, os, sys, zlib
H = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(H)))
from tokenizers import Tokenizer
TOK = {'qwen3': Tokenizer.from_file(os.path.join(ROOT, 'kalmar_complexity/tok/qwen3/tokenizer.json')),
       'gpt2': Tokenizer.from_file(os.path.join(ROOT, 'kalmar_complexity/tok/gpt2/tokenizer.json'))}

P = {
    'K-sl algorithm': ['ksl_alg.py'],
    'K-sl render ND': ['ksl_nd.py'],
    'K-sl render lean_seq': ['ksl_seq.py'],
    'parse (prompt -> sequent)': ['parse.py'],
    'K-sl algorithm + ND render': ['ksl_alg.py', 'ksl_nd.py'],
    'K-sl algorithm + lean_seq render': ['ksl_alg.py', 'ksl_seq.py'],
    'K-sl end to end (parse + algorithm + ND)': ['parse.py', 'ksl_alg.py', 'ksl_nd.py'],
    'K-sl end to end (parse + algorithm + lean_seq)': ['parse.py', 'ksl_alg.py', 'ksl_seq.py'],
    'K-tt algorithm': ['ktt_alg.py'],
    'K-tt render Lean': ['ktt_lean.py'],
    'K-tt algorithm + Lean render': ['ktt_alg.py', 'ktt_lean.py'],
    'K-tt end to end (parse + algorithm + Lean)': ['parse.py', 'ktt_alg.py', 'ktt_lean.py'],
    'K-sl per-step policy (state -> lean_seq action)': ['kpol.py'],
}
for c in ['copy', 'reverse', 'parity', 'parity_nb', 'sort', 'sort_nb', 'add', 'add_nb', 'eval', 'taut']:
    P['calib ' + c] = ['calib/%s.py' % c]
MECH = {'mech: kalmar/kalmar.py (builder + render)': 'kalmar/kalmar.py',
        'mech: tt_prover.py (whole file)': 'kalmar_complexity/ref/tt_prover.py',
        'mech: gen.py (K12 generator, all knobs)': 'gen.py',
        'mech: policy.py (per-step policy)': 'kalmar_complexity/programs/policy/policy.py'}


def sizes(src):
    b = src.encode()
    d = zlib.compressobj(9, zlib.DEFLATED, -15)
    defl = d.compress(b) + d.flush()
    xz = lzma.compress(b, format=lzma.FORMAT_RAW, filters=[{'id': lzma.FILTER_LZMA2, 'preset': 9 | lzma.PRESET_EXTREME}])
    return {'raw_bytes': len(b), 'deflate_bytes': len(defl), 'xz_bytes': len(xz),
            'qwen3_tokens': len(TOK['qwen3'].encode(src).ids), 'gpt2_tokens': len(TOK['gpt2'].encode(src).ids),
            'lines': src.count('\n') + (not src.endswith('\n'))}


def main():
    import python_minifier
    out = {}
    for name, files in P.items():
        src = ''.join(open(os.path.join(H, f)).read() for f in files)
        out[name] = {'files': files, **sizes(src)}
    for name, f in MECH.items():
        src = python_minifier.minify(open(os.path.join(ROOT, f)).read(), remove_literal_statements=True,
                                     rename_globals=False, rename_locals=True)
        out[name] = {'files': [f], 'method': 'python-minifier (literal statements removed, locals renamed)', **sizes(src)}
    json.dump(out, open(os.path.join(ROOT, 'artifacts/kc/python_sizes.json'), 'w'), indent=1)
    print(f"{'program':48} {'raw':>6} {'defl':>6} {'xz':>6} {'qwen3':>6} {'gpt2':>6} {'lines':>5}")
    for k, v in out.items():
        print(f"{k:48} {v['raw_bytes']:6} {v['deflate_bytes']:6} {v['xz_bytes']:6} {v['qwen3_tokens']:6} "
              f"{v['gpt2_tokens']:6} {v['lines']:5}")


if __name__ == '__main__':
    main()

"""BOTE fix test (run lean-seed2). (1) all held-out proofs that use BOTE + 1,000 others: render (lean_tok, both schemes), inverse == ND,
Lean accepts the literal text (lean_gate) and nd2lean --check-style translate (checker of record) accepts. (2) Negatives: every BOTE line
whose cited line is a negation/non-False formula instead of False (the exact looseness) must be rejected by Lean under the new rendering
and — for comparison — was accepted under the old `nA.elim`."""
import sys, json, random, re, collections
sys.path.insert(0, '.')
from lean_tok import LeanTokenizer, proof_tokens
from lean_gate import lean_check
from nd2lean import translate
from nd_verify import verify_text
recs = [json.loads(l) for l in open('data/heldout.jsonl')]
bote = [r for r in recs if 'BOTE' in r['proof']]
other = [r for r in recs if 'BOTE' not in r['proof']][:1000]
print('heldout', len(recs), 'with BOTE', len(bote))
rng = random.Random(0)
for mode in ('lean_seq', 'lean_rand'):
    tk = LeanTokenizer(mode); items = []; n_rt = 0
    for r in bote + other:
        nd = tk.decode(tk.shift_abs(tk.encode_proof(r['proof']), rng))
        n_rt += (nd == r['proof']); items.append((tk.statement(r['prompt']), tk.last_text))
    ok, w, c = lean_check(items)
    print(mode, 'round-trip', n_rt, '/', len(items), 'lean accepts', sum(ok), '/', len(ok), f'({c:.0f}s proc)')
    assert n_rt == len(items) == sum(ok)
# checker of record (nd2lean.translate, full multi-line rendering)
srcs = [translate(r['prompt'], r['proof']) for r in bote]
from nd2lean import lean_check as lc2
res = lc2(srcs, 40)
print('nd2lean.translate + Lean on BOTE held-out proofs:', sum(o for o, _ in res), '/', len(res))
assert sum(o for o, _ in res) == len(res)
# negatives: for each BOTE proof, retarget the BOTE citation to a line whose formula is a negation (in scope, same or outer depth) -> nd_verify rejects; Lean must reject too
from nd_verify.verify import parse_proof_tokens
def mutate(r):
    toks = r['proof'].split(); lines = parse_proof_tokens(toks)
    outs = []
    for ln in lines:
        if ln['rule'] != 'BOTE': continue
        for cand in lines:
            if cand['idx'] >= ln['idx'] or cand['formula'][0] != 'not': continue
            # rebuild proof text with the citation replaced
            new = []
            for l2 in lines:
                refs = list(l2['refs'])
                if l2['idx'] == ln['idx']: refs = [cand['idx']]
                from lean_tok import fnd
                new.append(f"N{l2['idx']} " + '| ' * l2['depth'] + f"{fnd(l2['formula'])} : {l2['rule']}" + ''.join(f' N{x}' for x in refs) + ' ;')
            outs.append(' '.join(new) + ' QED')
    return outs
negs = [(r['prompt'], p) for r in bote for p in mutate(r)]
negs = [(p, q) for p, q in negs if not verify_text(p + ' ' + q)[0]]
print('negatives (BOTE citing a negation; nd_verify rejects):', len(negs))
tk = LeanTokenizer('lean_seq'); items_new = []; items_old = []; n_struct = 0
negs = [(p, q) for p, q in negs if tk.decode(tk.encode_proof(q)) == q]     # in-scope citations only (out-of-scope ones are unbound names: rejected by the grammar)
print('  of which in scope (parse back):', len(negs))
for p, q in negs:
    ids = tk.encode_proof(q); nd = tk.decode(ids); assert nd == q, (nd, q)
    items_new.append((tk.statement(p), tk.last_text))
    items_old.append((tk.statement(p), re.sub(r'False\.elim (n\d+)', r'\1.elim', tk.last_text)))
ok_new, _, _ = lean_check(items_new); ok_old, _, _ = lean_check(items_old)
print('Lean accepts under NEW rendering (False.elim nA):', sum(ok_new), '/', len(ok_new))
print('Lean accepts under OLD rendering (nA.elim):      ', sum(ok_old), '/', len(ok_old))
srcs = []
for p, q in negs:
    try: srcs.append(translate(p, q))
    except Exception as e: n_struct += 1
res = lc2(srcs, 40)
print('nd2lean.translate (new) + Lean on negatives: accepted', sum(o for o, _ in res), '/', len(res), 'structural', n_struct)
json.dump({'heldout_bote': len(bote), 'negatives': len(negs), 'lean_ok_new': sum(ok_new), 'lean_ok_old': sum(ok_old), 'nd2lean_ok_new': sum(o for o, _ in res)}, open('artifacts/ls2/bote_test.json', 'w'), indent=1)

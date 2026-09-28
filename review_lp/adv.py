# reviewer's adversarial set: every term form x declared head (both spellings of ¬) x target type; filter vs Lean.
import sys, os, json, itertools, random, collections
sys.path.insert(0, os.path.expanduser('~/review/lean-prefilter')); sys.path.insert(0, os.path.expanduser('~/work/lean-prefilter/review_lp'))
from lean_prefilter import reject_reason, _split
from lean_tok import inverse, ParseFail
import rlean
random.seed(7)
# formulas as token strings, fully parenthesised
P, Q, R = 'P', 'Q', 'R'
def neg(a): return f'( ¬ {a} )'
def negf(a): return f'( {a} → False )'
def imp(a, b): return f'( {a} → {b} )'
def conj(a, b): return f'( {a} ∧ {b} )'
def disj(a, b): return f'( {a} ∨ {b} )'
F = 'False'
base = [P, Q, F, neg(P), negf(P), conj(P, Q), disj(P, Q), imp(P, Q), neg(conj(P, Q)), negf(conj(P, Q)), neg(neg(P)), negf(negf(P)), neg(negf(P)),
        imp(conj(P, Q), R), disj(neg(P), Q)]
def nd(f):   # token formula -> ND prompt formula
    return f.replace('¬', '~').replace('∧', '&').replace('∨', 'v').replace('→', '>').replace('False', 'F')
# targets: base plus the shapes the .elim rules produce, both spellings
def comps(f):
    out = set(base)
    for c in [R, F, P, neg(Q), negf(Q)]:
        out |= {imp(P, c), neg(P) if c == F else imp(P, c), imp(imp(P, imp(Q, c)), c), imp(imp(P, c), imp(imp(Q, c), c)),
                imp(imp(Q, c), imp(imp(P, c), c)), imp(imp(Q, imp(P, c)), c), imp(negf(P), c)}
    out |= {conj(Q, P), disj(Q, P), conj(neg(P), Q), conj(negf(P), Q), disj(negf(P), Q), neg(neg(P)), imp(neg(P), F), imp(negf(P), F), P, conj(P, P)}
    return sorted(out)
targets = comps(None)
tests = []
def add(prem, target, body):
    ps = ' , '.join(nd(p) for p in prem)
    prompt = f'THM {ps} SEQ {nd(target)} PRF'
    restate = ' '.join(f'have n{i+1} : {decl} := h{i+1} ;' for i, decl in enumerate(prem_decl_cur))
    text = f'{restate} have n50 : {target} := {body} ; exact n50'
    tests.append((prem, prompt, text))
# premises: pairs of base formulas; declared in both spellings where it has a ¬
def spell(f): return {f, f.replace('( ¬ P )', '( P → False )')}
for i, a in enumerate(base):
    for b in random.sample(base, 6):
        for da in spell(a):
            for db in spell(b):
                prem = [a, b]; prem_decl_cur = [da, db]
                for tgt in random.sample(targets, 14):
                    bodies = ['n1', 'n1.1', 'n1.2', 'n1.elim', 'n2.elim', 'n1 n2', 'n2 n1', '⟨ n1 , n2 ⟩', '⟨ n2 , n1 ⟩', 'Or.inl n1', 'Or.inr n2',
                              'Classical.byContradiction ( fun hh => n1 hh )',
                              f'( fun ( n60 : {P} ) => by exact n60 )', f'( fun ( n60 : {P} ) => by have n61 : False := n1 n60 ; exact ( n61 : False ) )',
                              f'( fun ( n60 : {neg(P)} ) => by have n61 : False := n60 n1 ; exact ( n61 : False ) )',
                              f'( fun ( n60 : {conj(P, Q)} ) => by have n61 : {Q} := n60.2 ; exact n61 )',
                              f'Or.elim n1 ( fun ( n60 : {P} ) => by have n61 : {tgt} := n2 n60 ; exact n61 ) ( fun ( n62 : {Q} ) => by have n63 : {tgt} := n62.elim ; exact n63 )',
                              f'Or.elim n1 ( fun ( n60 : {P} ) => by have n61 : {tgt} := n60.elim ; exact n61 ) ( fun ( n62 : {Q} ) => by have n63 : {tgt} := n2 n62 ; exact n63 )']
                    for body in bodies:
                        add(prem, tgt, body)
# keep texts in the strict grammar only (the filter's domain)
keep = []
seen = set()
for prem, prompt, text in tests:
    if (prompt, text) in seen: continue
    seen.add((prompt, text))
    try: inverse(_split(text))
    except Exception: continue
    keep.append((prompt, text))
from lean_tok import LeanTokenizer
tok = LeanTokenizer('lean_seq')
srcs = [f'{tok.statement(p)} {t}' for p, t in keep]
filt = [reject_reason(tok.statement(p), t) for p, t in keep]
print('generated', len(tests), 'in grammar', len(keep), 'filter rejects', sum(f is not None for f in filt), flush=True)
lean = rlean.check(srcs)
c = collections.Counter(); bad = []
for (p, t), f, l in zip(keep, filt, lean):
    c[(f is None, l)] += 1
    if f is not None and l: bad.append({'prompt': p, 'text': t, 'filter': f})
res = {'in_grammar': len(keep), 'cells(filter_pass, lean_ok)': {str(k): v for k, v in c.items()}, 'false_rejects': len(bad), 'examples': bad[:20],
       'filter_reasons_among_lean_rej': dict(collections.Counter(f for f, l in zip(filt, lean) if f is not None and l is False))}
json.dump(res, open(os.path.expanduser('~/review/lean-prefilter/review_lp/adv.json'), 'w'), indent=1, ensure_ascii=False)
print(json.dumps(res, ensure_ascii=False)[:3000])

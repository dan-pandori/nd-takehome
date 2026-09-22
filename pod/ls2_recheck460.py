"""Re-check the 460 known 'Lean accepts, nd_verify rejects' texts from run lean-format (artifacts/lf/gate_*.disagree.jsonl) under the
BOTE fix: the denoted ND proof is re-rendered (a) by lean_tok (training format, both schemes give the same Lean text up to names) and
sent to Lean via lean_gate; (b) by nd2lean.translate (checker of record) and sent to Lean. Also re-verifies nd_verify's verdict.
Output artifacts/ls2/recheck460.json with counts by disagreement kind."""
import sys, json, glob, re, collections
sys.path.insert(0, '.')
from lean_tok import LeanTokenizer
from lean_gate import lean_check
from nd2lean import translate, TranslationError, lean_check as lc2
from nd_verify import verify_text
recs = [json.loads(l) for f in sorted(glob.glob('artifacts/lf/gate_*.disagree.jsonl')) for l in open(f)]
print('records', len(recs))
def kind(r):
    if re.search(r'n\d+\.elim', r['lean_text']): return 'elim'
    reason = verify_text(r['prompt'] + ' ' + r['nd'])[1]
    if 'premise block' in reason: return 'missing-PR'
    return 'neg-unfold/other'
tk = LeanTokenizer('lean_seq')
kinds = [kind(r) for r in recs]
nd_ok = [verify_text(r['prompt'] + ' ' + r['nd'])[0] for r in recs]
print('nd_verify accepts (should be 0):', sum(nd_ok))
items_old = [(tk.statement(r['prompt']), r['lean_text']) for r in recs]
items_new = []
for r in recs:
    nd = tk.decode(tk.encode_proof(r['nd'])); assert nd == r['nd'], (nd, r['nd']); items_new.append((tk.statement(r['prompt']), tk.last_text))
ok_old, _, _ = lean_check(items_old); ok_new, _, _ = lean_check(items_new)
ok_rec = []; srcs = []; idx = []
for k, r in enumerate(recs):
    try: srcs.append(translate(r['prompt'], r['nd'])); idx.append(k); ok_rec.append(None)
    except TranslationError as e: ok_rec.append(('structural', str(e)))
res = lc2(srcs, 40)
for k, (o, m) in zip(idx, res): ok_rec[k] = ('lean', o)
tab = collections.defaultdict(collections.Counter)
for kd, a, b, c in zip(kinds, ok_old, ok_new, ok_rec):
    tab[kd]['n'] += 1; tab[kd]['lean_ok_old_text'] += bool(a); tab[kd]['lean_ok_new_render'] += bool(b)
    tab[kd]['record_lean_ok'] += (c[0] == 'lean' and c[1]); tab[kd]['record_structural'] += (c[0] == 'structural')
out = {k: dict(v) for k, v in tab.items()}; out['total'] = {'n': len(recs), 'lean_ok_old_text': sum(map(bool, ok_old)), 'lean_ok_new_render': sum(map(bool, ok_new)),
        'record_lean_ok': sum(c[0] == 'lean' and c[1] for c in ok_rec), 'record_structural': sum(c[0] == 'structural' for c in ok_rec), 'nd_verify_ok': sum(nd_ok)}
json.dump(out, open('artifacts/ls2/recheck460.json', 'w'), indent=1)
for k, v in out.items(): print(k, v)
with open('artifacts/ls2/recheck460.jsonl', 'w') as f:
    for r, kd, a, b, c in zip(recs, kinds, ok_old, ok_new, ok_rec):
        f.write(json.dumps({'prompt': r['prompt'], 'nd': r['nd'], 'kind': kd, 'old_text': r['lean_text'], 'lean_ok_old_text': bool(a), 'lean_ok_new_render': bool(b), 'record': list(c)}, ensure_ascii=False) + '\n')

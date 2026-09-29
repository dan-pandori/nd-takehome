#!/usr/bin/env python3
"""CI tests (run repo-hygiene): tokenizer and `lean_seq` round-trips, and the Lean judge on a fixed sample.

    python3 tests/test_roundtrip_judge.py            # needs Lean (~/.elan/bin/lean); `--no-lean` skips the judge part

Fixture `tests/fixtures/proofs150.jsonl`: 150 gold ND proofs (120 from data/lj/train_retain.jsonl chosen to cover every
rule, 30 ORE-heavy ones from data/r2/nec_nested_ore.jsonl).  Checks:
  1. token format (`rel`, `abs`): decode(encode_proof(p)) == p.
  2. `lean_seq`: decode(encode_proof(p)) == p; encode_proof(decode(ids)) == ids; the literal Lean text re-tokenised by
     splitting on spaces (and un-gluing `.1 .2 .elim`) gives back the same tokens; every name offset decodes the same.
  3. Lean judge, literal-text path (`lean_gate.gate`, what sampling uses): all 150 gold texts accepted; the canonical
     `Not.elim` example of the 2026-09-27 decision note accepted; negatives rejected -- each proof's text against a prompt
     whose conclusion has a different atom multiset (150), and each proof with its final `exact` dropped (150, a parse
     failure).
  4. Lean judge, ND path (`lean_judge.judge_many`, what hindsight relabels and dataset records use): all gold accepted,
     the canonical example accepted, the prompt-swapped negatives rejected.
"""
import json, os, random, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from tokenizer import Tokenizer
from lean_tok import LeanTokenizer

fails = []


def check(name, ok, detail=''):
    print(('PASS ' if ok else 'FAIL ') + name + ((' -- ' + str(detail)) if detail and not ok else ''))
    if not ok:
        fails.append(name)


rows = [json.loads(l) for l in open(os.path.join(HERE, 'tests/fixtures/proofs150.jsonl'))]
check('fixture has 150 rows', len(rows) == 150, len(rows))

# 1. token format
for mode in ('rel', 'abs'):
    tk = Tokenizer(mode)
    bad = [r['name'] for r in rows if tk.decode(tk.encode_proof(r['proof'])) != r['proof']]
    check(f'token format {mode}: decode(encode(p)) == p', not bad, bad[:3])

# 2. lean_seq
tk = LeanTokenizer('lean_seq')
rng = random.Random(0)
bad = {'nd': [], 'ids': [], 'text': [], 'shift': []}
texts = []
for r in rows:
    ids = tk.encode_proof(r['proof'])
    nd = tk.decode(ids)
    if nd != r['proof']:
        bad['nd'].append(r['name'])
    if nd.startswith('LEANPARSE') or tk.encode_proof(nd) != ids:
        bad['ids'].append(r['name'])
    toks = [tk.itos[i] for i in ids[:-1]]
    text = tk.last_text
    texts.append(text)
    re_toks = []
    for w in text.split():
        for suf in ('.elim', '.1', '.2'):
            if w.endswith(suf) and w != suf and w[:-len(suf)] in tk.stoi:
                re_toks += [w[:-len(suf)], suf]; break
        else:
            re_toks.append(w)
    if re_toks != toks:
        bad['text'].append(r['name'])
    for _ in range(3):
        if tk.decode(tk.shift_abs(ids, rng)) != r['proof']:
            bad['shift'].append(r['name']); break
check('lean_seq: decode(encode(p)) == p', not bad['nd'], bad['nd'][:3])
check('lean_seq: encode(decode(ids)) == ids', not bad['ids'], bad['ids'][:3])
check('lean_seq: literal text re-tokenises to the same tokens', not bad['text'], bad['text'][:3])
check('lean_seq: name offsets decode to the same proof', not bad['shift'], bad['shift'][:3])

if '--no-lean' in sys.argv:
    print('skipping the Lean judge (--no-lean)')
else:
    import tempfile
    os.environ['LEAN_GATE_LOG'] = os.path.join(tempfile.mkdtemp(prefix='ci_gate_'), 'gate.jsonl')
    import lean_gate, lean_judge
    # the canonical example: `~P |- P > Q` by `BOTE` on the negation line (nd2lean's `n1.elim`, i.e. Not.elim)
    canon_p = 'THM ( ~ P ) SEQ ( P > Q ) PRF'
    canon_nd = 'N1 ( ~ P ) : PR ; N2 ( P > Q ) : BOTE N1 ; QED'
    cids = tk.encode_proof(canon_nd)
    check('canonical Not.elim example decodes', tk.decode(cids) == canon_nd, tk.decode(cids))
    canon_text = tk.last_text

    atoms = lambda p: sorted(t for t in p.split('SEQ')[1].split() if t in 'PQRS')
    swap = []
    for i, r in enumerate(rows):
        for d in range(1, len(rows)):
            j = (i + d) % len(rows)
            if atoms(rows[j]['prompt']) != atoms(r['prompt']):
                swap.append(j); break
    prompts = [r['prompt'] for r in rows]
    nds = [r['proof'] for r in rows]
    # literal-text path
    out = lean_gate.gate(tk, prompts + [canon_p] + [prompts[j] for j in swap], nds + [canon_nd] + nds,
                         texts + [canon_text] + texts)
    acc = [not o.startswith('LEANREJ') for o in out]
    check('gate: 150/150 gold texts accepted', sum(acc[:150]) == 150, sum(acc[:150]))
    check('gate: canonical Not.elim text accepted', acc[150])
    check('gate: 0/150 prompt-swapped texts accepted', sum(acc[151:]) == 0, sum(acc[151:]))
    # dropping the final `exact nK` leaves text outside the strict grammar
    trunc = []
    for r in rows:
        ids = tk.encode_proof(r['proof'])
        trunc.append(tk.decode(ids[:-3] + [tk.eos]))
    res = lean_judge.judge_many(list(zip(prompts, trunc)))
    check('judge: 0/150 truncated proofs accepted', sum(ok for ok, _, _ in res) == 0,
          [t for t, (ok, _, _) in zip(trunc, res) if ok][:2])
    # ND path (fresh registry, so every string goes to Lean through nd2lean)
    lean_judge._registry.clear()
    res = lean_judge.judge_many(list(zip(prompts, nds)) + [(canon_p, canon_nd)] + [(prompts[j], nds[i]) for i, j in enumerate(swap)])
    ok = [x[0] for x in res]
    check('judge_many: 150/150 gold ND proofs accepted', sum(ok[:150]) == 150, sum(ok[:150]))
    check('judge_many: canonical Not.elim ND proof accepted', ok[150])
    check('judge_many: 0/150 prompt-swapped ND proofs accepted', sum(ok[151:]) == 0, sum(ok[151:]))

print(f'{len(fails)} failed' if fails else 'ALL PASS')
sys.exit(1 if fails else 0)

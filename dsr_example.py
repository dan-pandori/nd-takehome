import sys, json
sys.path.insert(0, '.')
from lean_tok import LeanTokenizer
from lean_gate import lean_check

NAME = 'train_depth3_f0_a1_124007'
rec = None
for l in open('data/p2/train_depth3_f0_a1.jsonl'):
    x = json.loads(l)
    if x.get('name') == NAME:
        rec = x; break
assert rec, 'record not found'

MODES = [('lean_seq', 'C0 `lean_seq` (control)', 'the control: premises re-stated, every `have` annotated, typed `fun` boxes'),
         ('lean_seq_noprem', 'R1 `lean_seq_noprem`', 'no premise re-statement -- the `have nK : A := hJ` lines are gone and `h1 h2` are cited directly'),
         ('lean_seq_nofml', 'R3 `lean_seq_nofml`', 'formula-free `have`s for IMPE / ANDE1 / ANDE2 / NEGE / R -- the type is left to inference'),
         ('lean_seq_intro', 'R2 `lean_seq_intro`', '`intro`-tactic boxes: `( by intro nS ; ... )` instead of a `fun` binder'),
         ('lean_seq_funbare', 'R4 `lean_seq_funbare`', 'bare-`fun` boxes: `( fun nS => by ... )` -- the binder stays, its TYPE ANNOTATION goes')]

out = []
texts = []
for mode, title, blurb in MODES:
    tok = LeanTokenizer(mode)
    ids = tok.encode_proof(rec['proof'])
    text = tok.text([tok.itos[i] for i in ids if i != tok.eos])
    back = tok.decode(ids, rec['prompt'])
    assert back == rec['proof'], f'{mode} round-trip FAILED\n{back}\n{rec["proof"]}'
    texts.append((tok.statement(rec['prompt']), text))
    out.append((mode, title, blurb, len(ids), tok.vocab_size, text))

def nd_pretty(p):
    parts = p.split(' ; ')
    return (' ;' + chr(10) + '        ').join(x.strip() for x in parts)


def wrap(t):
    """break the single-line Lean text after each TOP-LEVEL ' ; ' (depth 0) so the example reads."""
    out, depth, cur = [], 0, []
    for tok in t.split(' '):
        depth += (tok == '(') - (tok == ')')
        cur.append(tok)
        if tok == ';' and depth == 0:
            out.append(' '.join(cur)); cur = []
    if cur:
        out.append(' '.join(cur))
    return chr(10).join(out)


ok, wall, cpu = lean_check(texts)
assert all(ok), f'Lean rejected: {[m for (m,*_),o in zip(out,ok) if not o]}'

with open('examples/ds_rendering_four_modes.md', 'w') as f:
    f.write(f"""# One proof in all five ds-rendering modes

The same ND record of `data/p2/train_depth3_f0_a1.jsonl`, rendered by `lean_tok.py` in each mode. The brief asked
for four; **R4 `lean_seq_funbare` was added by addendum 1** to separate the two things R2 changes at once (the
binder's type annotation, and `fun` vs the `intro` tactic), so there are five here.

Regenerated and **verified** by `dsr_example.py`: every text below is accepted by **Lean 4.34** and every one
`inverse()`s back to the ND proof *exactly*. Token counts are `lean_tok.py`'s own, one symbol per token.

## The ND record (`nd_verify` / spec.md form)

```
name   {rec['name']}
prompt {rec['prompt']}
proof  {nd_pretty(rec['proof'])}
```

## The Lean statement (identical in every mode; it is the prompt)

```lean
{texts[0][0]}
```
""")
    for mode, title, blurb, ntok, vocab, text in out:
        f.write(f"\n## {title} — {ntok} tokens, vocabulary {vocab}\n\n{blurb}\n\n```lean\n{wrap(text)}\n```\n")
    base = out[0][3]
    f.write("\n## Token counts side by side\n\n| mode | tokens | vs control | vocabulary |\n|---|---|---|---|\n")
    for mode, title, _, ntok, vocab, _ in out:
        f.write(f"| `{mode}` | {ntok} | {ntok - base:+d} | {vocab} |\n")
    f.write(f"""
Only R2 needs a larger vocabulary (108 vs 107, the extra token being `intro`), which is why control checkpoints
still load in every other arm.

Two things in this table matter for reading the results:

- **R1 is much the shortest text (-18 tokens, -21%), and it is the worst arm.** That is the run's sharpest negative
  result stated in one line: the shortest rendering is not the best one, so the "cap + 1" horizon is not a property
  of text length.
- **R2 and R4 are the same length -- 78 tokens each.** They differ only in *which* piece of the typed `fun` binder
  is dropped: R4 keeps the binder and drops its type annotation, R2 replaces the whole binder with the `intro`
  tactic. So any R2-vs-R4 difference -- and the reductio gap between them is the run's cleanest single effect -- is
  **not** a length effect and cannot be explained by one arm simply writing less.

Lean checked all {len(texts)} texts in {wall:.2f} s wall ({cpu:.1f} s CPU).
""")
print('wrote examples/ds_rendering_four_modes.md')
for mode, title, _, ntok, vocab, _ in out:
    print(f'  {mode:22} {ntok:4d} tokens  vocab {vocab}  round-trip OK  Lean OK')

"""Reviewer's own render check: round-trip, token counts, text-length histograms,
Lean acceptance of literal rendered texts, and rejection of theorem-swapped negatives."""
import sys, os, json, random, collections
sys.path.insert(0, '/home/dan/work/ds-rendering')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lean_tok import LeanTokenizer
import lean_gate
from rv_norm import nd_len

N = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
lines = open('/home/dan/review/ds-rendering/data/p2/train_depth3_f0_a1.jsonl').readlines()
recs = [json.loads(l) for l in random.Random(7).sample(lines, N)]
del lines
MODES = [('c0', 'lean_seq'), ('r1', 'lean_seq_noprem'), ('r3', 'lean_seq_nofml'),
         ('r2', 'lean_seq_intro'), ('r4', 'lean_seq_funbare')]
base = None
rows = []
for arm, mode in MODES:
    tok = LeanTokenizer(mode)
    tok.shift = False
    ntok, rt, texts, thist = [], 0, [], collections.Counter()
    for r in recs:
        ids = tok.encode_prompt(r['prompt']) + tok.encode_proof(r['proof'])
        body = tok.encode_proof(r['proof'])
        ntok.append(len(body) - 1)            # proof tokens, <eos> excluded
        back = tok.decode(body, r['prompt'])
        rt += (back == r['proof'])
        texts.append(tok.last_text)
        thist[tok.last_text.count('have')] += 1
    mean = sum(ntok) / len(ntok)
    base = base or mean
    # Lean on 1000 literal rendered texts
    items = [(tok.statement(r['prompt']), t) for r, t in list(zip(recs, texts))[:1000]]
    ok, _, _ = lean_gate.lean_check(items)
    # 300 theorem-swapped negatives: keep the text, swap in another record's statement
    negs = [(tok.statement(recs[(i + 500) % len(recs)]['prompt']), texts[i]) for i in range(300)]
    nok, _, _ = lean_gate.lean_check(negs)
    rows.append((arm, mode, tok.vocab_size, rt, len(recs), mean, mean / base,
                 sum(ok), len(ok), sum(nok), len(nok), dict(sorted(thist.items()))))
    print('%-3s %-17s vocab %d  round-trip %d/%d  mean proof tokens %6.1f  ratio %.3f  '
          'Lean accepts %d/%d  swapped negatives accepted %d/%d' % rows[-1][:11], flush=True)
print()
print('have-line histogram of the literal text (same %d records)' % len(recs))
for r in rows:
    print('%-3s %s' % (r[0], ' '.join('%d:%d' % kv for kv in r[11].items())))
print()
print('ND length histogram of the same records: %s' %
      ' '.join('%d:%d' % kv for kv in sorted(collections.Counter(nd_len(r['proof']) for r in recs).items())))

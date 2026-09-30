#!/usr/bin/env python3
"""long-pool-2: literal-text Lean re-check set from the re-read dumps (LEAN_GATE_DUMP).

  python3 lpool2_recheck.py --out artifacts/lpool2/recheck/texts.jsonl   (then lean_check.py --texts <out> --out <x_lean>)

For every (checkpoint, pool, prompt) the gate accepted: the shortest accepted literal text (fewest `have`s, then characters)
-> kind 'acc'. Negative control: 3 gate-rejected texts per dump that reached Lean if any, else rejected by the pre-Lean
filter -> kind 'rej'. Also asserts that the accepted prompts of each dump equal the `solved` rows of its re-read file.
"""
import argparse, json, glob, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import record

ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--seed', type=int, default=0)
a = ap.parse_args(); record.save_config(vars(a), a.out)
rng = random.Random(a.seed); out, mism = [], []
for fn in sorted(glob.glob('artifacts/lpool2/dump/rr_*__new.jsonl') + glob.glob('artifacts/lpool2/dump/rr_*__cal.jsonl')):
    tag = os.path.basename(fn)[3:-6]
    best, rej = {}, []
    for l in open(fn):
        r = json.loads(l)
        if r['lean_ok']:
            k = (r['lean_text'].count('have '), len(r['lean_text']))
            if r['prompt'] not in best or k < best[r['prompt']][0]:
                best[r['prompt']] = (k, r['lean_text'])
        else:
            rej.append(r)
    rows = [json.loads(l) for l in open(f'artifacts/lpool2/rr/{tag}.jsonl')]
    solved = {r['prompt'] for r in rows if r['solved']}
    if solved != set(best):
        mism.append((tag, len(solved), len(best)))
    for p, (k, t) in best.items():
        out.append({'name': f'{tag}|acc|{len(out)}', 'prompt': p, 'lean_text': t, 'kind': 'acc', 'src': tag})
    lean_rej = [r for r in rej if r.get('lean') is not None] or rej
    for r in rng.sample(lean_rej, min(3, len(lean_rej))):
        out.append({'name': f'{tag}|rej|{len(out)}', 'prompt': r['prompt'], 'lean_text': r['lean_text'], 'kind': 'rej', 'src': tag})
os.makedirs(os.path.dirname(a.out), exist_ok=True)
with open(a.out, 'w') as f:
    for r in out:
        f.write(json.dumps(r) + '\n')
print(json.dumps({'acc': sum(r['kind'] == 'acc' for r in out), 'rej': sum(r['kind'] == 'rej' for r in out), 'dump_vs_rows_mismatch': mism}))

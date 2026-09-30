#!/usr/bin/env python3
"""support-state (reused by state-readouts for part A): independent Lean re-check of the counted proofs, on the VPS (Lean 4.34.1; the pods ran 4.34.0).

  python3 ss_recheck.py [--s1_sample 300]     # -> artifacts/state-readouts/recheck.json (+ a printed table)

Independent of the in-loop path: the theorem statement is built here from the prompt string (not by `lean_tok`),
each literal sampled text (`proofs[].lean_text`, the first literal text of every distinct accepted proof) is checked
in its OWN Lean process, and a proof counts only if Lean exits 0 with no `error` in its output.  Set: every distinct
counted proof of H (both seeds, both T) and S2, plus a seeded sample of S1.  Negative controls: each H proof with
one connective in its first `have` type flipped (∧ <-> ∨, or → -> ∧) must be rejected.
"""
import argparse, glob, json, os, random, re, subprocess, tempfile, collections
from concurrent.futures import ThreadPoolExecutor

LEAN = os.path.expanduser('~/.elan/bin/lean')
SYM = {'~': '¬', '&': '∧', 'v': '∨', '>': '→', 'F': 'False'}


def statement(prompt):
    body = prompt.split('THM', 1)[1].rsplit('PRF', 1)[0]
    prem, goal = body.split('SEQ')
    conv = lambda s: ' '.join(SYM.get(t, t) for t in s.split())
    prems = [p for p in (x.strip() for x in prem.split(' , ')) if p]
    hs = ' '.join(f'( h{i} : {conv(p)} )' for i, p in enumerate(prems, 1))
    return ' '.join(f'theorem t ( P Q R S : Prop ) {hs} : {conv(goal)} := by'.split())


def lean_ok(src):
    with tempfile.TemporaryDirectory() as d:
        fn = os.path.join(d, 'T.lean')
        open(fn, 'w').write(src + '\n')
        p = subprocess.run([LEAN, fn], capture_output=True, text=True, timeout=120)
        out = p.stdout + p.stderr
        return p.returncode == 0 and 'error' not in out


def mutate(tx):
    toks = tx.split()
    try:
        i = toks.index(':')           # first `have nK : <type> :=`
        j = toks.index(':=', i)
    except ValueError:
        return None
    for k in range(i + 1, j):
        if toks[k] in ('∧', '∨', '→'):
            toks[k] = {'∧': '∨', '∨': '∧', '→': '∧'}[toks[k]]
            return ' '.join(toks)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--s1_sample', type=int, default=300)
    ap.add_argument('--workers', type=int, default=2)
    a = ap.parse_args()
    prompts = {json.loads(l)['name']: json.loads(l)['prompt'] for l in open('data/sc/theorems.jsonl') if l.strip()}
    items = collections.defaultdict(list)       # group -> [(name, lean_text)]
    for fn in sorted(glob.glob('artifacts/state-readouts/*.s0.jsonl')):
        g = os.path.basename(fn).split('_')[0]
        g = 'S2' if g.startswith('S2') else g
        for l in open(fn):
            r = json.loads(l)
            for p in r['proofs']:
                items[g].append((r['name'], p['lean_text']))
    rng = random.Random(0)
    if len(items['S1']) > a.s1_sample:
        items['S1'] = rng.sample(items['S1'], a.s1_sample)
    jobs = [(g, n, tx, statement(prompts[n]) + ' ' + tx) for g in ('H', 'S2', 'S1') for n, tx in items[g]]
    neg = [(g, n, m, statement(prompts[n]) + ' ' + m) for g, n, tx, _ in jobs if g == 'H' for m in [mutate(tx)] if m]
    with ThreadPoolExecutor(a.workers) as ex:
        res = list(ex.map(lambda j: lean_ok(j[3]), jobs))
        nres = list(ex.map(lambda j: lean_ok(j[3]), neg))
    out = {'lean': subprocess.run([LEAN, '--version'], capture_output=True, text=True).stdout.strip(), 'groups': {}}
    for g in ('H', 'S2', 'S1'):
        rs = [ok for (gg, *_), ok in zip(jobs, res) if gg == g]
        out['groups'][g] = {'checked': len(rs), 'accepted': sum(rs),
                            'rejected': [(n, tx) for (gg, n, tx, _), ok in zip(jobs, res) if gg == g and not ok]}
        print(f'{g}: {sum(rs)} / {len(rs)} accepted')
    out['negative_controls'] = {'checked': len(nres), 'rejected': len(nres) - sum(nres),
                                'accepted': [(n, m) for (_, n, m, _), ok in zip(neg, nres) if ok]}
    print(f'negative controls (H, one connective flipped): {len(nres) - sum(nres)} / {len(nres)} rejected')
    json.dump(out, open('artifacts/state-readouts/recheck.json', 'w'), indent=1, ensure_ascii=False)


if __name__ == '__main__':
    main()

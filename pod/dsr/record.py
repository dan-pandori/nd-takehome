#!/usr/bin/env python3
"""Checker of record for run ds-rendering (runs ON the pod, where Lean and the artefacts are).

Two independent checks over every counted proof of this pod's arm:

 (A) the DENOTED ND proof through the UNMODIFIED nd2lean.py --check -- the checker of record renders the ND proof its
     OWN way (premises re-stated, every `have` annotated, `fun` boxes), so this is a check of the ND proof, not of the
     arm's rendering, and its verdict must not depend on the arm;
 (B) the LITERAL sampled Lean text -- the exact characters the model wrote, in the arm's own rendering -- through
     lean_gate.lean_check, which is what actually gated it in the loop.  coverage.py stores it in proofs[].text and
     eval_set/expert_iter/ladder_ei in lean_texts / found record `text`.

  python3 pod/dsr/record.py <arm>            # every artefact of that arm on this pod
Writes artifacts/dsr/record_<arm>.json and, for any disagreement, artifacts/dsr/record_<arm>_disagree.jsonl.
"""
import sys, os, glob, json, subprocess, collections, tempfile

sys.path.insert(0, '/workspace/nd-takehome')
A = 'artifacts/dsr'


def collect(arm):
    """-> list of {prompt, proof, text, src}: every counted proof this arm produced."""
    out = []
    for fn in sorted(glob.glob(f'{A}/cov_*_{arm}_s*.s0.jsonl')):
        for l in open(fn):
            r = json.loads(l)
            for p in r['proofs']:
                out.append({'prompt': r['prompt'], 'proof': p['proof'], 'text': p.get('text'), 'src': fn})
    for fn in sorted(glob.glob(f'{A}/mech_{arm}_s*.jsonl')) + sorted(glob.glob(f'{A}/held_{arm}_s*.jsonl')):
        for l in open(fn):
            r = json.loads(l)
            for p, t in zip(r['proofs'], (r.get('lean_texts') or [None] * len(r['proofs']))):
                out.append({'prompt': r['prompt'], 'proof': p, 'text': t, 'src': fn})
    for d in sorted(glob.glob(f'{A}/ei_d3_{arm}_s*')) + sorted(glob.glob(f'{A}/frz_d3_{arm}_s*')) \
            + sorted(glob.glob(f'{A}/la_T1_{arm}_s*')) + sorted(glob.glob(f'{A}/la_frz_{arm}_s*')):
        rounds = [int(os.path.basename(f)[6:-5]) for f in glob.glob(f'{d}/round_*.json')]
        if not rounds:
            continue
        R = max(rounds)
        for pool in ('found', 'found_transfer'):
            fn = f'{d}/{pool}_{R}.jsonl'
            if not os.path.exists(fn):
                continue
            for l in open(fn):
                r = json.loads(l)
                out.append({'prompt': r['prompt'], 'proof': r['proof'], 'text': r.get('text'), 'src': fn})
    return out


def main():
    arm = sys.argv[1]
    items = collect(arm)
    # de-duplicate on (prompt, proof): the same counted proof appears in several files
    seen = {}
    for it in items:
        seen.setdefault((it['prompt'], it['proof']), it)
    uniq = list(seen.values())
    print(f'{arm}: {len(items)} counted proof records, {len(uniq)} distinct (prompt, ND proof)', flush=True)

    # (A) the unmodified nd2lean.py --check on the denoted ND proofs
    tmp = tempfile.NamedTemporaryFile('w', suffix='.jsonl', delete=False, dir=A)
    for it in uniq:
        tmp.write(json.dumps({'prompt': it['prompt'], 'proof': it['proof']}) + '\n')
    tmp.close()
    rep = f'{A}/record_{arm}_nd2lean.jsonl'
    p = subprocess.run(['python3', 'nd2lean.py', '--check', tmp.name, '--out', rep, '--per_file', '40'],
                       capture_output=True, text=True)
    rows = [json.loads(l) for l in open(rep)] if os.path.exists(rep) else []
    cA = collections.Counter((r['nd_ok'], r['lean_ok']) for r in rows)
    os.unlink(tmp.name)

    # (B) Lean on the literal sampled text, in the arm's own rendering
    from lean_tok import LeanTokenizer
    from lean_gate import lean_check
    MODE = {'c0': 'lean_seq', 'r1': 'lean_seq_noprem', 'r3': 'lean_seq_nofml', 'r2': 'lean_seq_intro',
            'r4': 'lean_seq_funbare'}
    tok = LeanTokenizer(MODE[arm])
    lit = [it for it in uniq if it['text']]
    okB, wall, cpu = lean_check([(tok.statement(it['prompt']), it['text']) for it in lit])
    bad = [lit[i] for i, o in enumerate(okB) if not o]

    out = {'arm': arm, 'mode': MODE[arm], 'counted_records': len(items), 'distinct_proofs': len(uniq),
           'A_nd2lean_unmodified': {'n': len(rows), 'both_accept': cA[(True, True)],
                                    'nd_ok_lean_rej': cA[(True, False)], 'nd_rej_lean_ok': cA[(False, True)],
                                    'both_reject': cA[(False, False)],
                                    'stdout_tail': p.stdout.strip().splitlines()[-1:], 'stderr_tail': p.stderr[-300:]},
           'B_literal_text': {'n_with_text': len(lit), 'accepted': sum(okB), 'rejected': len(bad),
                              'no_text_stored': len(uniq) - len(lit), 'lean_wall_s': wall, 'lean_proc_s': cpu}}
    json.dump(out, open(f'{A}/record_{arm}.json', 'w'), indent=1)
    dis = [r for r in rows if r['nd_ok'] != r['lean_ok']]
    if dis or bad:
        with open(f'{A}/record_{arm}_disagree.jsonl', 'w') as f:
            for r in dis:
                f.write(json.dumps({'kind': 'nd2lean', **r}, ensure_ascii=False) + '\n')
            for r in bad:
                f.write(json.dumps({'kind': 'literal', **r}, ensure_ascii=False) + '\n')
    print(json.dumps(out, indent=1), flush=True)


if __name__ == '__main__':
    main()

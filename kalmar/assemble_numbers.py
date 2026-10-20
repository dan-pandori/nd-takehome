#!/usr/bin/env python3
"""Assemble the numbers.md § kalmar-pretrain text from the executor's drafts and the generated tables.

  python3 kalmar/assemble_numbers.py --draft artifacts/kalmar/numbers_src/section_draft.md \
      --ladder artifacts/kalmar/numbers_src/ladder_template.md --spend '$46.04' > section.md
(the two inputs are the executor's prose with placeholders; the result is `numbers.md` § kalmar-pretrain).

Fills: the compute table (artifacts/kalmar/compute.json, from `kalmar/compute.py`), the ladder tables
(artifacts/kalmar/ladder_stdout.txt), the exploratory tables (artifacts/kalmar/exploratory_stdout.txt) and the spend.
Fails if any placeholder is left.
"""
import argparse, collections, json, os, re

GPU = {('KAL-C', 'read'): '3090 (greedy) / A40 (sampled)', ('KAL-C', 'train'): 'RTX 3090',
       ('KAL-D', 'read'): '3090 (greedy) / A40 (sampled)', ('KAL-D', 'train'): 'RTX 3090',
       ('KAL-D', 'read (Addendum 3)'): 'A40',
       ('KAL-D+A', 'train'): 'A40 (s0, s2) / RTX 3090 (s1)', ('KAL-D+A', 'read'): 'A40 / RTX 3090 (s1 greedy)',
       ('KAL-D+A', 'read (Addendum 3)'): 'A40',
       ('control', 'read'): '3090 (greedy) / A40 (sampled)',
       ('ladder ei', 'ladder'): 'A40', ('ladder ei', 'ladder (OOM launch)'): 'A40', ('ladder frozen', 'ladder (OOM launch)'): 'A40', ('ladder ei', 'read'): 'A40', ('ladder frozen', 'ladder'): 'A40'}
ORDER = ['KAL-D', 'KAL-C', 'control', 'ladder ei', 'ladder frozen', 'KAL-D+A']


def compute_table(fn):
    rows = json.load(open(fn))['rows']
    per = collections.defaultdict(collections.Counter)
    for k, v in rows.items():
        arm, seed, ph = k.split('|')
        per[(arm.split(' snapshot')[0], ph)].update(v)
    out = ['| arm | phase | GPU-s | GPU | gen tokens | attempts | actions | train steps | train tokens | Lean checks |',
           '|---|---|---|---|---|---|---|---|---|---|']
    for (arm, ph) in sorted(per, key=lambda x: (ORDER.index(x[0]), x[1])):
        v = per[(arm, ph)]
        out.append(f"| {arm} | {ph} | {v['gpu_seconds']:,.0f} | {GPU.get((arm, ph), '?')} | {v['gen_tokens']:,.0f} | "
                   f"{v['attempts']:,.0f} | {v['actions']:,.0f} | {v['train_steps']:,.0f} | {v['train_tokens']:,.0f} | "
                   f"{v['lean_checks']:,.0f} |")
    out.append('| control (best-state, inherited) | train | 3 × ≈ 1,200 | A40 | — | — | — | 23,951 / 23,987 / 24,123 | '
               '≈ 3 × 0.44 B padded | — |')
    return '\n'.join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--draft', required=True)
    ap.add_argument('--ladder', required=True)
    ap.add_argument('--spend', required=True)
    ap.add_argument('--compute', default='artifacts/kalmar/compute.json')
    a = ap.parse_args()
    s = open(a.draft).read()
    lad = open(a.ladder).read()
    lad = lad.replace('LADDER_TABLES', open('artifacts/kalmar/ladder_stdout.txt').read().strip())
    lad = lad.replace('EXPLORATORY_TABLES', open('artifacts/kalmar/exploratory_stdout.txt').read().strip())
    # the compute table: from its header row to the inherited control row
    i = s.index('| arm | phase | GPU-s |')
    j = s.index('\n', s.index('| control (best-state, inherited) |'))
    s = s[:i] + compute_table(a.compute) + s[j:]
    secs = []
    for i in range(3):
        fn = f'artifacts/kalmar/eval/kalDA_s{i}_plain_k32.json'
        secs.append(f"{json.load(open(fn))['wall_s']:,.0f}" if os.path.exists(fn) else '—')
    lad = lad.replace('S1_SECS', ' / '.join(secs))
    s = s.replace('LADDER_SECTION', lad.strip()).replace('SPEND_TOTAL', a.spend)
    left = re.findall(r'\b[A-Z][A-Z_]{5,}\b', s)
    left = [x for x in left if x in ('LADDER_SECTION', 'LADDER_ROWS_NOTE', 'SPEND_TOTAL', 'LADDER_TABLES',
                                     'EXPLORATORY_TABLES', 'PLAIN_A_TABLE', 'PLAIN_A_LINE', 'S1_SECS')]
    assert not left, f'placeholders left: {left}'
    print(s.rstrip())


if __name__ == '__main__':
    main()

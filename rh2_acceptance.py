#!/usr/bin/env python3
"""repo-hygiene-2 acceptance: 0 lost files. Every file untracked by repo-hygiene (artifacts/ at 6123570e, artifacts/lpool
at 470d39e0) and every file this run untracked (artifacts/repo-hygiene-2/moved_tracked.txt, at cf5924e2) is either
tracked at <ref> with the same git blob, or has a MANIFEST row with the same git blob whose bucket copy passed the
sha256 check (artifacts/repo-hygiene-2/verify_bucket.tsv).   python3 rh2_acceptance.py [ref]   (stdout: a table)"""
import json, subprocess, sys
ref = sys.argv[1] if len(sys.argv) > 1 else 'HEAD'
git = lambda *a: subprocess.run(['git', *a], capture_output=True, text=True, check=True).stdout
def tree(commit, *paths):
    out = {}
    for l in git('ls-tree', '-r', commit, *paths).splitlines():
        meta, p = l.split('\t', 1); out[p] = meta.split()[2]
    return out
want = {**tree('6123570e', 'artifacts'), **tree('470d39e0', 'artifacts/lpool'),
        **tree('cf5924e2', *open('artifacts/repo-hygiene-2/moved_tracked.txt').read().split())}
now = tree(ref)
man = {json.loads(l)['path']: json.loads(l) for l in git('show', f'{ref}:artifacts/MANIFEST.jsonl').splitlines()}
ver = {l.split('\t')[0]: l.rstrip('\n').split('\t')[3] for l in open('artifacts/repo-hygiene-2/verify_bucket.tsv').readlines()[1:]}
c = {'tracked, same blob': 0, 'manifest, same blob, bucket sha256 ok': 0, 'LOST': 0}
for p, b in want.items():
    if now.get(p) == b: c['tracked, same blob'] += 1
    elif p in man and man[p]['git_blob'] == b and ver.get(p) == 'ok': c['manifest, same blob, bucket sha256 ok'] += 1
    else: c['LOST'] += 1; print('LOST', p, file=sys.stderr)
both = [p for p in man if p in now]
print(f'| {ref} | files | \n|---|---:|')
for k, v in c.items(): print(f'| {k} | {v:,} |')
print(f'| total checked | {len(want):,} |\n| manifest rows | {len(man):,} |\n| manifest rows also tracked (must be 0) | {len(both)} |')
print(f"| manifest rows with bucket sha256 ok | {sum(ver.get(p) == 'ok' for p in man):,} |")

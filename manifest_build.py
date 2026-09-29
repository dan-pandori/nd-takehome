#!/usr/bin/env python3
"""repo-hygiene-2: split the files repo-hygiene untracked into small (back into git) and bulk (manifest rows).

    python3 manifest_build.py [ckpts/final.pt data/r1/prompts.jsonl ...]

Untracked set U = artifacts/ at 6123570e (parent of e844a8ea, same tree as 3bfdec15) + the 5 artifacts/lpool/ files at
470d39e0 (untracked in 22d0837c). Bulk rule: fetch_artifacts.is_bulk. The optional arguments are currently tracked
bulk files (ckpts/, data/) that this run uploads to repo-hygiene-2/git_tip/<path> and untracks.
Writes artifacts/MANIFEST.jsonl (sha256 from the git blob; verified against the bucket separately with
fetch_artifacts.py --verify-remote) and artifacts/repo-hygiene-2/restore.tsv (small files: path, commit, blob, bytes).
`run` = the producing run where known: `run_src` says how (bucket_copy = the same content already sat at
<run>/artifacts/... before repo-hygiene; dir = every bucket_copy row of that artifacts/<dir>/ names this one run;
trailer = Run-id trailer of the commit that added the file; convention = the take-home and round-2 directory names
below, which predate Run-id trailers and bucket run paths: p2/p3 = take-home phases 2-3, rN = round2-runN)."""
import collections, hashlib, json, os, subprocess, sys
from fetch_artifacts import is_bulk

BUCKET = 'hf://buckets/dan-pandori/nd-rl'
SRC = [('6123570e', 'artifacts'), ('470d39e0', 'artifacts/lpool')]
IDX = [os.path.expanduser('~/runs/repo-hygiene/index_post.tsv'), os.path.expanduser('~/runs/repo-hygiene/index_longpool.tsv')]


CONVENTION = {'artifacts/p2/': 'takehome', 'artifacts/p3/': 'takehome', 'artifacts/ign/': 'ignition',
              'ckpts/final.pt': 'takehome', 'ckpts/stage1_abs.pt': 'takehome', 'data/train.jsonl.gz': 'takehome',
              'data/p2/run5_': 'round2-run5', **{f'{d}/r{i}/': f'round2-run{i}' for d in ('artifacts', 'data') for i in range(1, 6)}}


def convention(p):
    hit = [r for k, r in CONVENTION.items() if p.startswith(k)]
    return (hit[0], 'convention') if hit else (None, None)


def git(*a):
    return subprocess.run(['git', *a], capture_output=True, text=True, check=True).stdout


def blob_sha256(blobs):
    """sha256 of each blob via one `git cat-file --batch`."""
    p = subprocess.Popen(['git', 'cat-file', '--batch'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    out = {}
    for b in blobs:
        p.stdin.write((b + '\n').encode()); p.stdin.flush()
        sha, typ, n = p.stdout.readline().split()
        h, left = hashlib.sha256(), int(n)
        while left:
            c = p.stdout.read(min(left, 1 << 20)); h.update(c); left -= len(c)
        p.stdout.read(1)
        out[b] = h.hexdigest()
    p.stdin.close(); p.wait()
    return out


def run_of_commit(path):
    c = git('log', '--diff-filter=A', '--format=%h', '--', path).split()
    if not c:
        return None, None
    body = git('log', '-1', '--format=%B', c[-1])
    rid = [l.split(':', 1)[1].strip() for l in body.splitlines() if l.startswith('Run-id:')]
    return (rid[0] if rid else None), c[-1]


def main():
    U = {}
    for commit, prefix in SRC:
        for l in git('ls-tree', '-r', '-l', commit, prefix).splitlines():
            meta, path = l.split('\t', 1)
            _, _, blob, size = meta.split()
            U[path] = dict(path=path, bytes=int(size), git_blob=blob, commit=commit)
    idx = {}
    for f in IDX:
        for l in open(f).read().splitlines()[1:]:
            path, size, blob, xet, cls, ok, copies = (l.split('\t') + [''])[:7]
            idx[path] = dict(cls=cls, ok=ok == '1', copies=[c for c in copies.split(',') if c], blob=blob)
    assert set(U) == set(idx), (len(U), len(idx), sorted(set(U) ^ set(idx))[:5])
    assert all(idx[p]['blob'] == U[p]['git_blob'] and idx[p]['ok'] for p in U)

    # producing run: direct bucket copy, else a directory whose bucket copies all name one run
    direct = {p: idx[p]['copies'][0].split('/')[0] for p in U if idx[p]['cls'] == 'run_path'}
    dirruns = collections.defaultdict(set)
    for p, r in direct.items():
        dirruns[os.path.dirname(p)].add(r)

    bulk = sorted(p for p in U if is_bulk(p, U[p]['bytes']))
    small = sorted(p for p in U if p not in set(bulk))
    sha = blob_sha256(sorted({U[p]['git_blob'] for p in bulk}))
    rows = []
    for p in bulk:
        r = U[p]
        run, src = direct.get(p), 'bucket_copy'
        if run is None:
            d = dirruns.get(os.path.dirname(p), set())
            run, src = (next(iter(d)), 'dir') if len(d) == 1 else convention(p)
        rows.append(dict(path=p, uri=f'{BUCKET}/repo-hygiene/git_tip/{p}', bytes=r['bytes'], sha256=sha[r['git_blob']],
                         run=run, run_src=src, git_blob=r['git_blob'], git_commit=r['commit'],
                         also_at=[f'{BUCKET}/{c}' for c in idx[p]['copies'][:3]]))
    # currently tracked bulk files (ckpts/, data/) moved by this run
    for p in sys.argv[1:]:
        meta = git('ls-tree', '-l', 'HEAD', p).split()
        assert meta, p
        blob, size = meta[2], int(meta[3])
        assert is_bulk(p, size), p
        run, c = run_of_commit(p)
        src = 'trailer' if run else None
        if run is None:
            run, src = convention(p)
        rows.append(dict(path=p, uri=f'{BUCKET}/repo-hygiene-2/git_tip/{p}', bytes=size,
                         sha256=blob_sha256([blob])[blob], run=run, run_src=src,
                         git_blob=blob, git_commit=git('rev-parse', '--short=8', 'HEAD').strip(), also_at=[]))
    with open('artifacts/MANIFEST.jsonl', 'w') as f:
        for r in sorted(rows, key=lambda r: r['path']):
            f.write(json.dumps(r) + '\n')
    os.makedirs('artifacts/repo-hygiene-2', exist_ok=True)
    with open('artifacts/repo-hygiene-2/restore.tsv', 'w') as f:
        f.write('path\tcommit\tgit_blob\tbytes\n')
        for p in small:
            f.write(f"{p}\t{U[p]['commit']}\t{U[p]['git_blob']}\t{U[p]['bytes']}\n")
    c = collections.Counter(r['run_src'] for r in rows)
    print(f"U: {len(U)} files, {sum(u['bytes'] for u in U.values()):,} bytes")
    print(f"small (restore): {len(small)} files, {sum(U[p]['bytes'] for p in small):,} bytes")
    print(f"manifest: {len(rows)} rows, {sum(r['bytes'] for r in rows):,} bytes; run known by {dict(c)}")


if __name__ == '__main__':
    main()

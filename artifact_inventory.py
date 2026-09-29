#!/usr/bin/env python3
"""Inventory of the git-tracked `artifacts/` tree against the HF bucket (run repo-hygiene).

Needs `hf_xet` (the `hf` CLI's own interpreter has it):
  PY=~/.local/share/uv/tools/huggingface-hub/bin/python

  $PY artifact_inventory.py hash   --rev 3bfdec15 --out INV.tsv [--upload]   # stream blobs, xet-hash, mirror upload
  $PY artifact_inventory.py match  --inv INV.tsv --ls bucket_ls.json --out ARTIFACTS_INDEX.tsv

`hash` materialises every blob from `git cat-file` (never from the working tree: a sparse worktree lacks most of
it, and the tree may differ from the revision) into a scratch dir in chunks of ~800 MB, hashes each file with
`hf_xet.hash_files` (the hash the bucket lists as `xet_hash`), and with `--upload` syncs the chunk to
MIRROR/<path> before deleting it. `match` classifies each file: `run_path` = same size and hash at
`<run>/artifacts/<rel>` somewhere in the bucket; `elsewhere` = same hash under another path; `absent`. It also
reports whether the mirror copy exists with the same size and hash; the removal happens only if it does for all.
"""
import argparse, json, os, shutil, subprocess, sys
from collections import defaultdict

MIRROR = 'hf://buckets/dan-pandori/nd-rl/repo-hygiene/git_tip'
MIRROR_KEY = 'repo-hygiene/git_tip/'
CHUNK = 800 * 2**20


def tracked(rev):
    out = subprocess.run(['git', 'ls-tree', '-r', '-l', '-z', rev, 'artifacts'], capture_output=True, check=True).stdout
    rows = []
    for rec in out.decode().split('\0'):
        if not rec:
            continue
        meta, path = rec.split('\t', 1)
        mode, typ, blob, size = meta.split()
        if typ == 'blob':
            rows.append((path, int(size), blob))
    return rows


def cmd_hash(a):
    import hf_xet
    rows = tracked(a.rev)
    done = {}
    if os.path.exists(a.out):
        for line in open(a.out):
            p, s, b, h = line.rstrip('\n').split('\t')
            done[p] = h
    todo = [r for r in rows if r[0] not in done]
    print(f'{len(rows)} tracked files, {sum(r[1] for r in rows)} bytes; {len(todo)} to hash', flush=True)
    chunks, cur, cur_b = [], [], 0
    for r in todo:
        cur.append(r); cur_b += r[1]
        if cur_b >= CHUNK:
            chunks.append(cur); cur, cur_b = [], 0
    if cur:
        chunks.append(cur)
    cat = subprocess.Popen(['git', 'cat-file', '--batch'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    with open(a.out, 'a') as fout:
        for ci, chunk in enumerate(chunks):
            if os.path.exists(a.stage):
                shutil.rmtree(a.stage)
            paths = []
            for path, size, blob in chunk:
                cat.stdin.write((blob + '\n').encode()); cat.stdin.flush()
                hdr = cat.stdout.readline().split()
                assert hdr[0].decode() == blob and int(hdr[2]) == size, (path, hdr)
                data = cat.stdout.read(size); cat.stdout.read(1)
                dst = os.path.join(a.stage, path)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                with open(dst, 'wb') as f:
                    f.write(data)
                paths.append(dst)
            infos = hf_xet.hash_files(paths)
            for (path, size, blob), info in zip(chunk, infos):
                assert info.file_size == size, path
                fout.write(f'{path}\t{size}\t{blob}\t{info.hash}\n')
            if a.upload:
                subprocess.run(['hf', 'buckets', 'sync', os.path.join(a.stage, 'artifacts'), MIRROR + '/artifacts'],
                               check=True, stdout=subprocess.DEVNULL)
            fout.flush()
            print(f'chunk {ci + 1}/{len(chunks)}: {len(chunk)} files, {sum(r[1] for r in chunk)} bytes'
                  + (' uploaded' if a.upload else ''), flush=True)
    cat.stdin.close(); cat.wait()
    if os.path.exists(a.stage):
        shutil.rmtree(a.stage)


def cmd_match(a):
    ls = [e for e in json.load(open(a.ls)) if e.get('type') == 'file']
    by_path = {e['path']: e for e in ls}
    by_hash = defaultdict(list)
    for e in ls:
        if not e['path'].startswith(MIRROR_KEY):
            by_hash[e['xet_hash']].append(e['path'])
    inv = [l.rstrip('\n').split('\t') for l in open(a.inv)]
    cls = defaultdict(lambda: [0, 0])
    mirror_ok = mirror_bad = 0
    with open(a.out, 'w') as fo:
        fo.write('path\tbytes\tgit_blob\txet_hash\tclass\tmirror_ok\trun_copies\n')
        for path, size, blob, h in inv:
            size = int(size); rel = path[len('artifacts/'):]
            same = [p for p in by_hash.get(h, []) if by_path[p]['size'] == size]
            at_run = [p for p in same if p.endswith('/artifacts/' + rel) and p.count('/') == rel.count('/') + 2]
            c = 'run_path' if at_run else ('elsewhere' if same else 'absent')
            cls[c][0] += 1; cls[c][1] += size
            m = by_path.get(MIRROR_KEY + path)
            ok = bool(m and m['size'] == size and m['xet_hash'] == h)
            mirror_ok += ok; mirror_bad += not ok
            fo.write(f'{path}\t{size}\t{blob}\t{h}\t{c}\t{int(ok)}\t{",".join(sorted(at_run or same)[:3])}\n')
    print(f'{"class":10s} {"files":>6s} {"bytes":>12s}')
    for c in ('run_path', 'elsewhere', 'absent'):
        print(f'{c:10s} {cls[c][0]:6d} {cls[c][1]:12d}')
    print(f'total      {len(inv):6d} {sum(v[1] for v in cls.values()):12d}')
    print(f'mirror copy verified (size+xet hash): {mirror_ok}/{len(inv)}; missing or mismatched: {mirror_bad}')
    return 0 if mirror_bad == 0 else 1


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest='cmd', required=True)
    h = sp.add_parser('hash'); h.add_argument('--rev', required=True); h.add_argument('--out', required=True)
    h.add_argument('--stage', default='/home/dan/runs/repo-hygiene/stage'); h.add_argument('--upload', action='store_true')
    m = sp.add_parser('match'); m.add_argument('--inv', required=True); m.add_argument('--ls', required=True)
    m.add_argument('--out', required=True)
    a = ap.parse_args()
    sys.exit({'hash': cmd_hash, 'match': cmd_match}[a.cmd](a) or 0)

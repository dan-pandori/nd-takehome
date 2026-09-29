#!/usr/bin/env python3
"""Credential scan of public-bucket objects and local files (run repo-hygiene-2). Prints no secret, only where and what kind.

    python3 scan_secrets.py --bucket repo-hygiene/ --bucket repo-hygiene-2/ --report hits.tsv   # stream bucket objects
    python3 scan_secrets.py FILE...                                                              # local files

Two detectors, applied to the raw bytes and, for .gz / .tgz / .tar.gz, to the decompressed bytes (tar members too):
  pattern  hf_ / gh*_ / github_pat_ tokens, Anthropic sk-ant-, RunPod rpa_ keys and RUNPOD_API_KEY=..., PEM private
           keys, OpenSSH public keys (reported, kind ssh_public), oauth_token / accessToken / refreshToken fields
  known    the exact credentials present on this machine: env vars named *TOKEN*/*KEY*/*SECRET*, `gh auth token`,
           values in ~/.config/nd-rl/env, ~/.claude/.credentials.json token fields, lines of ~/.ssh private keys.
           Only values >= 16 characters count; they are held in memory and never written anywhere.
Exit 1 if anything is found. publish_artifacts.py runs the same scan on every file before it uploads it."""
import argparse, glob, gzip, io, json, os, re, subprocess, sys, tarfile, urllib.request
from concurrent.futures import ThreadPoolExecutor

PATTERNS = [
    ('hf_token', rb'\bhf_[A-Za-z0-9]{30,}'),
    ('github_token', rb'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})'),
    ('anthropic_key', rb'sk-ant-[A-Za-z0-9_-]{20,}'),
    ('runpod_key', rb'\brpa_[A-Za-z0-9]{20,}|RUNPOD_API_KEY\s*[=:]\s*["\']?[A-Za-z0-9_-]{16,}'),
    ('private_key', rb'-----BEGIN [A-Z ]*PRIVATE KEY-----'),
    ('ssh_public', rb'ssh-(?:rsa|ed25519|dss) AAAA[0-9A-Za-z+/]{40,}'),
    ('oauth_field', rb'(?:oauth_token|accessToken|refreshToken|access_token|refresh_token)["\']?\s*[:=]\s*["\']?[A-Za-z0-9._-]{20,}'),
]
RX = [(k, re.compile(p)) for k, p in PATTERNS]
OVERLAP = 512


def known_secrets():
    vals = {}
    for k, v in os.environ.items():
        if re.search(r'TOKEN|KEY|SECRET', k) and len(v) >= 16:
            vals['env:' + k] = v
    try:
        t = subprocess.run(['gh', 'auth', 'token'], capture_output=True, text=True, timeout=30).stdout.strip()
        if len(t) >= 16: vals['gh_auth_token'] = t
    except Exception:
        pass
    for f in [os.path.expanduser('~/.config/nd-rl/env')]:
        if os.path.exists(f):
            for l in open(f):
                m = re.match(r'\s*(?:export\s+)?([A-Za-z_]+)\s*=\s*["\']?([^"\'\s]+)', l)
                if m and len(m.group(2)) >= 16 and re.search(r'TOKEN|KEY|SECRET|PASS', m.group(1)):
                    vals['nd-rl/env:' + m.group(1)] = m.group(2)
    cf = os.path.expanduser('~/.claude/.credentials.json')
    if os.path.exists(cf):
        def walk(o, pre):
            if isinstance(o, dict):
                for k, v in o.items(): walk(v, pre + '.' + k)
            elif isinstance(o, str) and re.search(r'[Tt]oken', pre) and len(o) >= 16:
                vals['claude_credentials' + pre] = o
        walk(json.load(open(cf)), '')
    for f in glob.glob(os.path.expanduser('~/.ssh/*')):
        try:
            txt = open(f).read()
        except Exception:
            continue
        if 'PRIVATE KEY' in txt:
            for i, l in enumerate(txt.splitlines()):
                if len(l) >= 40 and 'PRIVATE KEY' not in l:
                    vals[f'ssh:{os.path.basename(f)}:line{i}'] = l
    return {k: v.encode() for k, v in vals.items()}


KNOWN = None


def scan_stream(chunks, known):
    """chunks: iterable of bytes. Returns a set of hit kinds."""
    hits, tail = set(), b''
    for c in chunks:
        buf = tail + c
        for k, rx in RX:
            if rx.search(buf): hits.add(k)
        for k, v in known.items():
            if v in buf: hits.add('known:' + k)
        tail = buf[-OVERLAP:]
    return hits


def chunked(f, n=1 << 20):
    return iter(lambda: f.read(n), b'')


def scan_bytes_obj(name, data, known):
    hits = scan_stream([data[i:i + (1 << 22)] for i in range(0, len(data), 1 << 22)] or [b''], known)
    low = name.lower()
    try:
        if low.endswith(('.tgz', '.tar.gz', '.tar')):
            with tarfile.open(fileobj=io.BytesIO(data)) as t:
                for m in t.getmembers():
                    if m.isfile():
                        hits |= {f'{h} (in {m.name})' for h in scan_stream(chunked(t.extractfile(m)), known)}
        elif low.endswith('.gz'):
            hits |= {h + ' (gunzipped)' for h in scan_stream(chunked(gzip.GzipFile(fileobj=io.BytesIO(data))), known)}
    except Exception as e:
        hits.add(f'unreadable archive: {type(e).__name__}')
    return hits


def fetch(uri_path):
    from fetch_artifacts import url
    with urllib.request.urlopen(url('hf://buckets/dan-pandori/nd-rl/' + uri_path), timeout=600) as r:
        return r.read()


def list_bucket(prefix):
    from record import hf_bin
    p = subprocess.run([hf_bin(), 'buckets', 'list', 'hf://buckets/dan-pandori/nd-rl/' + prefix.rstrip('/'), '-R',
                        '--json'], capture_output=True, text=True, timeout=900)
    return [e['path'] for e in json.loads(p.stdout) if e.get('type') == 'file']


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('files', nargs='*')
    ap.add_argument('--bucket', action='append', default=[], help='bucket prefix below dan-pandori/nd-rl/ to stream')
    ap.add_argument('--report', help='TSV of every scanned object and its hits')
    ap.add_argument('--jobs', type=int, default=8)
    a = ap.parse_args()
    known = known_secrets()
    print(f'{len(known)} known credentials loaded (values not shown); {len(RX)} patterns', file=sys.stderr)
    items = [('file', f) for f in a.files] + [('bucket', p) for pre in a.bucket for p in list_bucket(pre)]

    def one(it):
        kind, name = it
        try:
            data = open(name, 'rb').read() if kind == 'file' else fetch(name)
            return len(data), scan_bytes_obj(name, data, known)
        except Exception as e:
            return -1, {f'ERROR {type(e).__name__}: {e}'}
    with ThreadPoolExecutor(a.jobs) as ex:
        res = list(ex.map(one, items))
    nhit = sum(1 for _, h in res if h)
    if a.report:
        with open(a.report, 'w') as f:
            f.write('source\tobject\tbytes\thits\n')
            for (k, n), (b, h) in zip(items, res):
                f.write(f"{k}\t{n}\t{b}\t{';'.join(sorted(h))}\n")
    for (k, n), (b, h) in zip(items, res):
        if h: print(f'HIT {k} {n}: {sorted(h)}')
    print(f'{len(items)} objects, {sum(max(b, 0) for b, _ in res):,} bytes scanned; {nhit} with hits', file=sys.stderr)
    sys.exit(1 if nhit else 0)


if __name__ == '__main__':
    main()

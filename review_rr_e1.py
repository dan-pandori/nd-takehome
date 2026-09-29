# Reviewer's own E1 check: every ckpt_saved row in the live registry files -> download URI -> md5 == row md5.
import json, glob, hashlib, subprocess, os, sys
REG = os.path.expanduser('~/review/results-registry/artifacts/results-registry/registry')
def md5(p):
    h = hashlib.md5(); f = open(p, 'rb')
    for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()
rows = []
for fn in sorted(glob.glob(REG + '/2026*.jsonl')):
    for l in open(fn):
        r = json.loads(l)
        if r['metric'] == 'ckpt_saved': rows.append((os.path.basename(fn), r))
print('ckpt_saved rows:', len(rows))
flip = None
for fn, r in rows:
    uri = r['ckpt_uri']; loc = f'/tmp/rrrev/dl/{os.path.basename(r["ckpt"])}'
    os.makedirs('/tmp/rrrev/dl', exist_ok=True)
    p = subprocess.run(['hf', 'buckets', 'cp', uri, loc], capture_output=True, text=True)
    got = md5(loc) if p.returncode == 0 and os.path.exists(loc) else 'DOWNLOAD_FAILED:' + p.stderr[-200:]
    print(fn, r['ckpt'], r['value'], os.path.getsize(loc) if os.path.exists(loc) else None, r['ckpt_md5'], got, 'OK' if got == r['ckpt_md5'] else 'FAIL', r['labels'].get('upload_s'))
    flip = (loc, r['ckpt_md5'])
# negative control on my own checker: flip one byte of the last download
loc, want = flip
b = bytearray(open(loc, 'rb').read()); b[len(b)//2] ^= 1; open(loc + '.flip', 'wb').write(b)
print('byte-flip control: md5 equal?', md5(loc + '.flip') == want, '(must be False)')

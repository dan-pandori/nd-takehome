"""results-registry tests: record.py rows, checkpoint upload on save, merge / query, and the negative controls.
    python3 tests/test_registry.py            offline cases only (no network, no torch)
    python3 tests/test_registry.py --online   + real uploads to hf://…/results-registry/ckpts/_test/ and a bad bucket
With torch importable (a pod), model.save_ckpt is exercised too.  Each case runs in a fresh interpreter, since
record.py keeps per-process state (its row file, the config).  Exit status 1 if any case fails."""
import hashlib, json, os, subprocess, sys, tempfile, textwrap
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONLINE = '--online' in sys.argv
FAILS = []


def run(code, env=None, expect_fail=False):
    e = {k: v for k, v in os.environ.items() if not k.startswith('ND_')}
    e.update(env or {})
    p = subprocess.run([sys.executable, '-c', 'import sys; sys.path.insert(0, %r)\n' % HERE + textwrap.dedent(code)],
                       capture_output=True, text=True, env=e, cwd=e.get('_CWD', HERE))
    return p


def case(name, ok, detail=''):
    print(('PASS ' if ok else 'FAIL ') + name + ('' if ok else f'  -- {detail[-600:]}'), flush=True)
    if not ok:
        FAILS.append(name)


def rows(d):
    out = []
    for f in sorted(os.listdir(d)):
        out += [json.loads(l) for l in open(os.path.join(d, f)) if l.strip()]
    return out


tmp = tempfile.mkdtemp(prefix='rr_test_')
ck = os.path.join(tmp, 'ckpts', 'x.pt')
os.makedirs(os.path.dirname(ck))
open(ck, 'wb').write(os.urandom(5000))
data = os.path.join(tmp, 'd.jsonl')
open(data, 'w').write('{"prompt": "x"}\n')

# 1. offline publish: sidecar without URI, one ckpt_saved row, md5 right
reg = os.path.join(tmp, 'reg1')
p = run(f"""
import record
record.publish_ckpt({ck!r}, step=7)
""", {'ND_OFFLINE': '1', 'ND_REGISTRY_DIR': reg, 'ND_RUN_ID': 'rr-test'})
md5 = hashlib.md5(open(ck, 'rb').read()).hexdigest()
sc = json.load(open(ck + '.upload.json')) if os.path.exists(ck + '.upload.json') else {}
r = rows(reg) if os.path.isdir(reg) else []
case('offline publish writes sidecar + row', p.returncode == 0 and sc.get('md5') == md5 and sc.get('uri') is None
     and len(r) == 1 and r[0]['metric'] == 'ckpt_saved' and r[0]['ckpt_md5'] == md5 and r[0]['labels'].get('step') == 7,
     p.stderr + str(sc) + str(r))

# 2. negative control: no ND_RUN_ID and not offline -> raises, nothing uploaded
p = run(f"""
import record
record.publish_ckpt({ck!r})
""", {'ND_REGISTRY_DIR': os.path.join(tmp, 'reg2')})
case('publish without ND_RUN_ID raises', p.returncode != 0 and 'ND_RUN_ID is not set' in p.stderr, p.stderr)

# 3. record(): config, labels, env defaults, data md5, ND_REGISTRY=0
reg = os.path.join(tmp, 'reg3')
p = run(f"""
import record
record.set_config({{'seed': 4, 'data': {data!r}, 'lr': 1e-3}}, role='stage1')
record.record('heldout_greedy_acc', 0.9, n=10, split='heldout', L='5', source='s.json')
record.record('x', 1, seed=9, arm='explicit')
""", {'ND_OFFLINE': '1', 'ND_REGISTRY_DIR': reg, 'ND_RUN_ID': 'rr-test', 'ND_ARM': 'envarm'})
r = rows(reg) if os.path.isdir(reg) else []
dm = hashlib.md5(open(data, 'rb').read()).hexdigest()
case('record fills config / labels / defaults', p.returncode == 0 and len(r) == 2
     and r[0]['seed'] == 4 and r[0]['arm'] == 'envarm' and r[0]['role'] == 'stage1' and r[0]['split'] == 'heldout'
     and r[0]['labels'] == {'L': '5'} and r[0]['data_md5'] == dm and r[0]['config']['lr'] == 1e-3
     and r[1]['seed'] == 9 and r[1]['arm'] == 'explicit' and r[0]['run_id'] == 'rr-test', p.stderr + str(r))
reg = os.path.join(tmp, 'reg3b')
p = run("""
import record
record.record('x', 1)
""", {'ND_OFFLINE': '1', 'ND_REGISTRY_DIR': reg, 'ND_REGISTRY': '0'})
case('ND_REGISTRY=0 writes nothing', p.returncode == 0 and not os.path.exists(reg), p.stderr)

# 4. round_stats roles: round 1 = init, later = rl, --no_train = frozen; greedy on stats['ckpt']
reg = os.path.join(tmp, 'reg4')
p = run("""
import record
s = lambda r, ck: {'round': r, 'ckpt': ck, 'k': 32, 'heldout_greedy': {'n': 10, 'solved': 9, 'rate': 0.9, 'by_len': {}},
                   'targets_cum': {'n': 20, 'solved': 5, 'rate': 0.25, 'by_len': {}}, 'target_sample_acc': 0.1}
record.round_stats(s(1, 'ckpts/s1.pt'), 'r1.json', init='ckpts/s1.pt')
record.round_stats(s(2, 'ckpts/ei_r1.pt'), 'r2.json', init='ckpts/s1.pt')
record.round_stats(s(2, 'ckpts/s1.pt'), 'f2.json', init='ckpts/s1.pt', frozen=True)
""", {'ND_OFFLINE': '1', 'ND_REGISTRY_DIR': reg, 'ND_RUN_ID': 'rr-test'})
r = rows(reg) if os.path.isdir(reg) else []
g = [(x['role'], x['labels']['round'], x['ckpt']) for x in r if x['metric'] == 'heldout_greedy_acc']
case('round_stats roles', p.returncode == 0 and g == [('init', 1, 'ckpts/s1.pt'), ('rl', 2, 'ckpts/ei_r1.pt'),
     ('frozen', 2, 'ckpts/s1.pt')] and {x['metric'] for x in r} == {'heldout_greedy_acc', 'targets_solved_cum',
     'targets_sample_acc'}, p.stderr + str(g))

# 5. merge: duplicates dropped, query filters
reg = os.path.join(tmp, 'reg5')
os.makedirs(reg)
base = {'schema': 1, 'run_id': 'a', 'metric': 'heldout_greedy_acc', 'value': 0.5, 'role': 'stage1', 'labels': {}}
with open(os.path.join(reg, 'f1.jsonl'), 'w') as f:
    f.write(json.dumps({**base, 'utc': '1'}) + '\n' + json.dumps({**base, 'utc': '2'}) + '\n')
    f.write(json.dumps({**base, 'role': 'rl', 'value': 0.7, 'labels': {'L': '3'}}) + '\n')
p = run(f"""
import registry_merge as m, glob
rs = m.load(sorted(glob.glob({reg!r} + '/*.jsonl')))
print(len(rs), len([r for r in rs if m.match(r, ['role=stage1,init', 'L='])]), len([r for r in rs if m.match(r, ['L=3'])]),
      len([r for r in rs if m.match(r, ['role!=rl'])]))
""")
case('merge dedupe + query', p.returncode == 0 and p.stdout.split() == ['2', '1', '1', '1'], p.stdout + p.stderr)

if ONLINE:
    # 6. real upload; the downloaded copy has the recorded md5; a one-byte flip does not (negative control)
    reg = os.path.join(tmp, 'reg6')
    p = run(f"""
import record
info = record.publish_ckpt({ck!r})
print(info['uri'])
""", {'ND_REGISTRY_DIR': reg, 'ND_RUN_ID': 'results-registry', 'ND_REGISTRY_SYNC': '0',
      '_CWD': tmp})
    uri = p.stdout.strip().splitlines()[-1] if p.stdout.strip() else ''
    dl = os.path.join(tmp, 'dl.pt')
    q = subprocess.run(['hf', 'buckets', 'cp', uri, dl], capture_output=True, text=True) if uri else None
    got = hashlib.md5(open(dl, 'rb').read()).hexdigest() if os.path.exists(dl) else None
    case('upload -> download md5 equal', p.returncode == 0 and uri.endswith('/results-registry/ckpts/_ext/x.pt')
     and got == md5, p.stderr + uri + str(got))
    if got:
        b = bytearray(open(dl, 'rb').read()); b[100] ^= 1
        case('negative control: flipped byte fails md5', hashlib.md5(bytes(b)).hexdigest() != md5)
    # 7. bad bucket -> raises (and writes no sidecar claiming an upload)
    if os.path.exists(ck + '.upload.json'):
        os.remove(ck + '.upload.json')
    p = run(f"""
import record
record.publish_ckpt({ck!r})
""", {'ND_REGISTRY_DIR': os.path.join(tmp, 'reg7'), 'ND_RUN_ID': 'results-registry',
      'ND_BUCKET': 'hf://buckets/dan-pandori/no-such-bucket-rr-test'})
    case('negative control: upload to a missing bucket raises', p.returncode != 0 and 'upload FAILED' in p.stderr
         and not os.path.exists(ck + '.upload.json'), p.stderr)
    subprocess.run(['hf', 'buckets', 'rm', '-y', uri.replace('hf://buckets/', '')], capture_output=True)

try:
    import torch  # noqa: F401
    HAVE_TORCH = True
except ImportError:
    HAVE_TORCH = False
if HAVE_TORCH:
    # 8. model.save_ckpt refuses before writing when ND_RUN_ID is unset; offline it writes + records
    out = os.path.join(tmp, 'ckpts', 'm.pt')
    code = f"""
from model import GPT, save_ckpt
m = GPT(vocab=16, d=16, n_layer=1, n_head=2, max_len=8)
save_ckpt({out!r}, m, 'rel', extra={{'step': 3}})
"""
    p = run(code, {'ND_REGISTRY_DIR': os.path.join(tmp, 'reg8')})
    case('save_ckpt without ND_RUN_ID raises before writing', p.returncode != 0 and not os.path.exists(out), p.stderr)
    p = run(code, {'ND_REGISTRY_DIR': os.path.join(tmp, 'reg8'), 'ND_OFFLINE': '1'})
    case('save_ckpt offline writes ckpt + sidecar', p.returncode == 0 and os.path.exists(out + '.upload.json'), p.stderr)
else:
    print('SKIP save_ckpt cases (no torch here)')

print(f'{len(FAILS)} failed' if FAILS else 'ALL PASS')
sys.exit(1 if FAILS else 0)

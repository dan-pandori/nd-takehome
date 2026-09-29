# Reviewer's own E2 negative controls on record.publish_ckpt / run_id (the non-torch half of model.save_ckpt).
import os, sys, subprocess, json
R = os.path.expanduser('~/review/results-registry')
open('/tmp/rrrev/fake.pt', 'wb').write(os.urandom(4096))
def run(env, code):
    e = {k: v for k, v in os.environ.items() if not k.startswith('ND_')}
    e.update(env, ND_REGISTRY_DIR='/tmp/rrrev/reg', ND_REGISTRY_SYNC='0')
    p = subprocess.run([sys.executable, '-c', f'import sys; sys.path.insert(0, {R!r}); import record; ' + code],
                       env=e, capture_output=True, text=True, timeout=600)
    return p.returncode, (p.stderr.strip().splitlines() or [''])[-1][:160]
print('b1 run_id(required) with ND_RUN_ID unset:', run({}, 'record.run_id(required=True)'))
print('b2 publish_ckpt with ND_RUN_ID unset:', run({}, "record.publish_ckpt('/tmp/rrrev/fake.pt')"))
print('b3 ND_OFFLINE=0 counts as online (unset id must still raise):', run({'ND_OFFLINE': '0'}, "record.publish_ckpt('/tmp/rrrev/fake.pt')"))
if os.path.exists('/tmp/rrrev/fake.pt.upload.json'): os.remove('/tmp/rrrev/fake.pt.upload.json')
print('c  non-existent bucket:', run({'ND_RUN_ID': 'rr-review-negctl', 'ND_BUCKET': 'hf://buckets/dan-pandori/no-such-bucket-rrrev'},
      "record.publish_ckpt('/tmp/rrrev/fake.pt')"), 'sidecar written?', os.path.exists('/tmp/rrrev/fake.pt.upload.json'))
print('d  ND_OFFLINE=1 opt-out:', run({'ND_OFFLINE': '1'}, "print(record.publish_ckpt('/tmp/rrrev/fake.pt'))"),
      json.load(open('/tmp/rrrev/fake.pt.upload.json')))

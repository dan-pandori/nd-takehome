"""Reviewer (compute-record): what rows survive (a) normal exit, (b) an uncaught exception, (c) SIGTERM, (d) timeout(1)
(SIGTERM), for a script that registers its config and counts work.  CPU only, offline, temp registry."""
import glob, json, os, signal, subprocess, sys, tempfile, time
HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BODY = ("import sys, time; sys.path.insert(0, %r); import record; record.save_config({'seed': 3}, None, arm='T'); "
        "record.phase('sample', round=1); record.count(gen_tokens=100, attempts=4); time.sleep(0.3); "
        "record.phase('sample', round=2); record.count(gen_tokens=7); time.sleep(0.3); ").replace('%r', repr(HERE))
res = {}
for name, tail, kill in [('normal', 'pass', None), ('exception', "raise RuntimeError('boom')", None),
                         ('sigterm', 'time.sleep(30)', signal.SIGTERM), ('sigint', 'time.sleep(30)', signal.SIGINT)]:
    d = tempfile.mkdtemp(); env = {**os.environ, 'ND_OFFLINE': '1', 'ND_REGISTRY_DIR': d, 'ND_REGISTRY_SYNC': '0', 'ND_RUN_ID': 'rv'}
    p = subprocess.Popen([sys.executable, '-c', BODY + tail], env=env, stderr=subprocess.DEVNULL)
    if kill:
        time.sleep(2.0); p.send_signal(kill)
    p.wait()
    rows = [json.loads(l) for f in glob.glob(f'{d}/*.jsonl') for l in open(f)]
    res[name] = {'rc': p.returncode, 'rows': sorted((r['metric'], r['value'] if r['metric'] != 'gpu_seconds' else 's', r['labels'].get('phase'),
                                                      r['labels'].get('round'), r['labels'].get('status')) for r in rows)}
    print(name, res[name])
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'term.json'), 'w'), indent=1)

"""C1(d)/C2(b): read embedded training args + param counts from checkpoints, torch-free
(uses /home/dan/work/best-state/review_bs/ptread.py, numpy only)."""
import sys, glob, os, hashlib, json, numpy as np
sys.path.insert(0, '/home/dan/work/best-state/review_bs'); import ptread
KEYS = ['data', 'train', 'mode', 'fmt', 'steps', 'batch', 'lr', 'cap', 'n_layer', 'n_embd', 'n_head', 'd_model', 'layers', 'seed', 'max_lines', 'warmup', 'schedule']
out = {}
for p in sorted(glob.glob('/home/dan/work/claim-audit/audit/raw/ckpts/*.pt')):
    d = ptread.load(p)
    sd = d.get('state') or d.get('model') or {}
    npar = int(sum(np.prod(v.shape) for k, v in sd.items() if hasattr(v, 'shape')))
    a = dict((d.get('extra') or {}).get('args') or {}); a.update({'cfg_'+k: v for k, v in (d.get('cfg') or {}).items()}); a['tok_mode'] = d.get('tok_mode'); a['extra_n_params'] = (d.get('extra') or {}).get('n_params'); a['extra_records'] = (d.get('extra') or {}).get('records'); a['extra_pairs'] = (d.get('extra') or {}).get('pairs')
    if not isinstance(a, dict): a = vars(a) if hasattr(a, '__dict__') else {'raw': str(a)[:300]}
    out[os.path.basename(p)] = {'md5': hashlib.md5(open(p, 'rb').read()).hexdigest(), 'params': npar, 'top_keys': list(d.keys()), 'args': {k: (v if isinstance(v, (int, float, str, bool, type(None))) else str(v)) for k, v in a.items()}}
    del d, sd
json.dump(out, open('/home/dan/work/claim-audit/audit/out/c1c2_ckpt_args.json', 'w'), indent=1)
allk = sorted(set(k for v in out.values() for k in v['args']))
for k in ['params'] + allk:
    vals = [str(v['params'] if k == 'params' else v['args'].get(k, '-'))[:28] for v in out.values()]
    if k == 'params' or len(set(vals)) > 1 or k in ('data', 'train', 'steps', 'batch', 'lr', 'cap'): print(f'{k:16s}', *[f'{x:28s}' for x in vals])
print(' ' * 16, *[f'{n[:28]:28s}' for n in out])

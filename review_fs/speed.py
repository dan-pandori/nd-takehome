import json, glob, re, collections
def info(f):
    R = [json.loads(l) for l in open(f)]
    a = [r for r in R if r.get('kind') == 'args'][0]
    st = [r for r in R if r.get('kind') == 'step']
    d = [r for r in R if r.get('kind') == 'done']
    s0 = ([r for r in st if r['step'] >= 400] or [st[0]])[0]; s1 = st[-1]
    if s1['step'] == s0['step']: s0 = dict(step=0, secs=(d[0].get('first_step_s') or 0) if d else 0, val_full_s=0)
    ms = 1000 * ((s1['secs'] - s1.get('val_full_s', 0)) - (s0['secs'] - s0.get('val_full_s', 0))) / (s1['step'] - s0['step'])
    return dict(f=f.split('/')[-1][:-6], impl=a['args']['impl'], bs=a['args']['bs'], steps=a['args']['steps'], ms=ms,
                total=d[0]['secs'] if d else None, val=d[0]['val_full_s'] if d else None, first=d[0].get('first_step_s') if d else None,
                setup=d[0].get('setup_s') if d else None, peak=(d[0].get('peak_mem') or 0) / 2**30 if d else None,
                waste=(a.get('computed_tokens') or 0) / (a.get('useful_tokens') or 1), legwaste=(a.get('legacy_computed_tokens') or 0) / (a.get('useful_tokens') or 1),
                useful=a.get('useful_tokens'), utc=d[0]['utc'] if d else None)
rows = [info(f) for f in sorted(glob.glob('artifacts/fs/m_*.jsonl') + glob.glob('artifacts/fs/b*.jsonl'))]
for r in rows:
    print(f"{r['f']:22s} {r['impl']:6s} bs{r['bs']:<4d} {r['steps']:5d} st  {r['ms']:6.1f} ms/step(steady)  total {r['total'] or 0:6.1f}s val {r['val'] or 0:5.1f} first {r['first'] or 0:5.1f} setup {r['setup'] or 0:4.1f} peak {r['peak'] or 0:.2f}GiB waste {r['waste']:.3f} legpad {r['legwaste']:.3f} {r['utc']}")

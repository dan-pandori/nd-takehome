#!/usr/bin/env python3
"""Reviewer's second pass for round3-run1: per-schema acquisition, what precedes the first required pattern proof in the mix arms,
transfer pools, concentration of drift-coverage hits, Stage-1 checkpoints. Own helpers only (review_run5_recount.py) + nd_verify.

  ROOT=~/review/round3-run1 python3 review_r3_1_extra.py
"""
import json, os, sys, glob, re, collections, zipfile, pickle

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.expanduser(os.environ.get('ROOT', HERE))
sys.path.insert(0, HERE)
from review_run5_recount import rkey, thm_of_prompt, parse_proof, prune, normalise, p_reductio, max_depth, rd
sys.path.insert(0, ROOT)
from nd_verify import verify_text

OUT = os.path.join(HERE, 'artifacts', 'review_r3_1')
A = os.path.join(ROOT, 'artifacts', 'r3_1')
D = os.path.join(ROOT, 'data', 'r3_1')


def feats(proof):
    ls = parse_proof(proof)
    pr = prune(ls)
    by = {l['idx']: l for l in pr}
    dn_of_negi = any(l['rule'] == 'DN' and l['refs'] and by.get(l['refs'][0], {}).get('rule') == 'NEGI' for l in pr)
    return {'depth3': max_depth(pr) >= 3, 'reductio': p_reductio(pr), 'dn': any(l['rule'] == 'DN' for l in pr), 'negi': any(l['rule'] == 'NEGI' for l in pr),
            'dn_of_negi': dn_of_negi, 'last_rule': pr[-1]['rule'], 'pruned': len(pr)}


def first_rounds(fn):
    first = {}
    for x in rd(fn):
        k = (x['name'], normalise(x['proof']))
        if k not in first or x['round'] < first[k]:
            first[k] = x['round']
    return first


res = {}
for pat in ['depth3', 'reductio']:
    req = {x['name']: x for x in rd(f'{D}/{pat}_req.jsonl')}
    nb = {x['name']: x for x in rd(f'{D}/{pat}_nb.jsonl')}
    tr = {x['name']: x for x in rd(f'{D}/{pat}_req_transfer.jsonl')}
    for s in range(20, 28):
        for c in ['req', 'mix', 'drift']:
            arm = f'ei_{pat}_s{s}_{c}'
            r = {}
            first = first_rounds(f'{A}/{arm}/found_8.jsonl')
            F = {k: feats(k[1]) for k in first}
            # required pattern targets by schema / by length / by alt
            patr = {}
            for (n, p), rnd in first.items():
                if n in req and F[(n, p)][pat]:
                    patr[n] = min(patr.get(n, 99), rnd)
            if pat == 'reductio':
                r['req_pattern_by_schema_r8'] = dict(collections.Counter(req[n]['schema'] for n in patr))
                r['req_pattern_by_schema_by_round'] = {rr: dict(collections.Counter(req[n]['schema'] for n in patr if patr[n] <= rr)) for rr in range(1, 9)}
                r['req_pattern_by_minlen_r8'] = dict(collections.Counter(req[n]['min_lines_ub'] for n in patr))
            else:
                r['req_pattern_by_minlen_r8'] = dict(collections.Counter(req[n]['min_lines_ub'] for n in patr))
                r['req_pattern_by_r10alt_r8'] = dict(collections.Counter(str(req[n]['r10_min_lines_ub']) for n in patr))
                r['req_pattern_by_src_r8'] = dict(collections.Counter(req[n]['src'] for n in patr))
            fr = min(patr.values()) if patr else None
            r['first_required_pattern_round'] = fr
            # what was in the found set (hence trainable) strictly before the first required pattern proof
            lim = fr if fr else 99
            nbk = [k for k in first if k[0] in nb]
            r['nb_distinct_proofs_before'] = sum(1 for k in nbk if first[k] < lim)
            for f in ['depth3', 'reductio', 'dn', 'negi', 'dn_of_negi']:
                r[f'nb_proofs_{f}_before'] = sum(1 for k in nbk if first[k] < lim and F[k][f])
                r[f'nb_targets_{f}_before'] = len({k[0] for k in nbk if first[k] < lim and F[k][f]})
                r[f'nb_proofs_{f}_r8'] = sum(1 for k in nbk if F[k][f])
            r['nb_first_pattern_round'] = min((first[k] for k in nbk if F[k][pat]), default=None)
            r['nb_pattern_targets_by_round'] = [len({k[0] for k in nbk if F[k][pat] and first[k] <= rr}) for rr in range(1, 9)]
            if fr:
                ex = sorted((rnd, n, p) for (n, p), rnd in first.items() if n in req and F[(n, p)][pat] and rnd == fr)[:2]
                r['first_required_examples'] = [{'round': a, 'name': b, 'schema': req[b].get('schema'), 'thm': req[b]['thm'], 'proof': c_} for a, b, c_ in ex]
            # transfer pool (required transfer targets): own count from found_transfer_8, every record verified
            tf = f'{A}/{arm}/found_transfer_8.jsonl'
            tp, ts, vf = set(), set(), 0
            if os.path.exists(tf):
                for x in rd(tf):
                    if x['name'] not in tr or x['prompt'] != tr[x['name']]['prompt'] or not verify_text(x['prompt'] + ' ' + x['proof'])[0]:
                        vf += 1; continue
                    ts.add(x['name'])
                    if feats(x['proof'])[pat]:
                        tp.add(x['name'])
            r['transfer_n'] = len(tr); r['transfer_solved_cum'] = len(ts); r['transfer_pattern_cum'] = len(tp); r['transfer_bad_records'] = vf
            res[arm] = r
            print(arm, {k: v for k, v in r.items() if k not in ('first_required_examples', 'req_pattern_by_schema_by_round')}, flush=True)

# concentration of coverage hits
conc = {}
for fn in sorted(glob.glob(f'{A}/cov_*.jsonl') + glob.glob(f'{A}/dcov_*.jsonl')):
    key = os.path.basename(fn).replace('.s0.jsonl', '')
    pat = 'depth3' if 'depth3' in key else 'reductio'
    per = {}
    for x in rd(fn):
        h = sum(p['count'] for p in x['proofs'] if feats(p['proof'])[pat])
        if h:
            per[x['name']] = h
    if per:
        reqs = {x['name']: x for x in rd(f'{D}/{pat}_req.jsonl')}
        conc[key] = {'hits': sum(per.values()), 'targets': len(per), 'top_target_hits': max(per.values()),
                     'per_target': {n: [h, reqs[n].get('schema'), reqs[n]['min_lines_ub']] for n, h in sorted(per.items(), key=lambda t: -t[1])}}
res['_cov_concentration'] = conc
for k, v in conc.items():
    print(k, v['hits'], v['targets'], v['top_target_hits'], list(v['per_target'].items())[:4])


# Stage-1 checkpoints: read `extra`/args by unpickling data.pkl with stubbed tensors
class Stub:
    def __init__(self, *a, **k): pass
    def __call__(self, *a, **k): return Stub()
    def __setstate__(self, s): pass


class U(pickle.Unpickler):
    def find_class(self, mod, name):
        if mod.startswith('torch') or mod.startswith('numpy'):
            return Stub
        if mod == 'collections' and name == 'OrderedDict':
            return collections.OrderedDict
        return super().find_class(mod, name)

    def persistent_load(self, pid):
        return Stub()


ck = {}
for fn in sorted(glob.glob(f'{ROOT}/ckpts/r3_1/stage1_*.pt')):
    try:
        z = zipfile.ZipFile(fn)
        pk = [n for n in z.namelist() if n.endswith('data.pkl')][0]
        obj = U(z.open(pk)).load()
        meta = {k: v for k, v in obj.items() if k != 'model' and not isinstance(v, (Stub, collections.OrderedDict))} if isinstance(obj, dict) else str(type(obj))
        ck[os.path.basename(fn)] = json.loads(json.dumps(meta, default=str))
    except Exception as e:
        ck[os.path.basename(fn)] = f'ERR {e}'
res['_stage1_ckpts'] = ck
for k, v in ck.items():
    print(k, str(v)[:600])
json.dump(res, open(f'{OUT}/extra.json', 'w'), indent=1, sort_keys=True)

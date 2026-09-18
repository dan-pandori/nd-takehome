#!/usr/bin/env python3
"""Reviewer: split disjointness by renaming class (own key: lexicographic minimum over all 24 atom permutations; a second,
stronger key also sorts the premises) between every TRAINING file and every EVALUATION pool.
Training files: data/train.jsonl, every artifacts/ladder/*/mix_*.jsonl (which contain the accumulated target proofs, the
relabelled by-products and the T5 injection records), relabelled_*.jsonl, inject_records.jsonl, data/ladder/rl_targets.jsonl.
Evaluation pools: data/ladder/transfer.jsonl, data/heldout.jsonl, targets/validation_36.jsonl, data/transfer.jsonl (take-home).
Also: every mix record whose prompt is an RL target carries a proof that is in that arm's found set (no generator proof trained on);
every mix proof verifies; line-count distribution of non-target mix records (cap 6 on supervised data)."""
import json, glob, os, sys, collections
from rv_recount import rv_key, prompt_to_thm, rv_nlines, rv_norm, A
from nd_verify import verify_text

def keys_of(fn, strong):
    ks = set()
    for l in open(fn):
        if not l.strip(): continue
        r = json.loads(l)
        thm = r['thm'] if 'thm' in r else prompt_to_thm(r['prompt'])
        ks.add(rv_key(thm, strong))
    return ks

cache = {}
def key_prompt(p, strong):
    k = (p, strong)
    if k not in cache:
        cache[k] = rv_key(prompt_to_thm(p), strong)
    return cache[k]

def main():
    res = {}
    for strong in (False, True):
        ev = {n: keys_of(fn, strong) for n, fn in (('ladder_transfer', 'data/ladder/transfer.jsonl'), ('heldout', 'data/heldout.jsonl'),
                                                   ('validation36', 'targets/validation_36.jsonl'), ('takehome_transfer', 'data/transfer.jsonl'))}
        tr = {'rl_targets': keys_of('data/ladder/rl_targets.jsonl', strong)}
        print('strong' if strong else 'plain', {n: len(v) for n, v in ev.items()}, flush=True)
        # Stage-1 train
        ktrain = set()
        for l in open('data/train.jsonl'):
            ktrain.add(key_prompt(json.loads(l)['prompt'], strong))
        tr['stage1_train'] = ktrain
        tgt_prompts = {json.loads(l)['prompt'] for l in open('data/ladder/rl_targets.jsonl')}
        train_prompts = None
        for d in sorted(glob.glob(f'{A}/la_*/')):
            ks = set()
            for fn in sorted(glob.glob(d + 'mix_*.jsonl')) + sorted(glob.glob(d + 'relabelled_*.jsonl')) + glob.glob(d + 'inject_records.jsonl'):
                for l in open(fn):
                    ks.add(key_prompt(json.loads(l)['prompt'], strong))
            if ks:
                tr[d.split('/')[-2]] = ks
        for tn, tk in tr.items():
            for en, ek in ev.items():
                n = len(tk & ek)
                res[f"{'strong' if strong else 'plain'}|{tn}|{en}"] = n
                if n:
                    print('  OVERLAP', 'strong' if strong else 'plain', tn, en, n, list(tk & ek)[:2], flush=True)
        # pools among themselves
        print('  rl_targets x ladder_transfer:', len(tr['rl_targets'] & ev['ladder_transfer']), ' ladder_transfer x stage1_train:', len(ev['ladder_transfer'] & ktrain),
              ' rl_targets x stage1_train:', len(tr['rl_targets'] & ktrain), ' rl_targets x heldout:', len(tr['rl_targets'] & ev['heldout']), flush=True)
    json.dump(res, open('review_out/disjoint.json', 'w'), indent=1)
    # provenance of mix records
    train_set = set()
    for l in open('data/train.jsonl'):
        r = json.loads(l); train_set.add((r['prompt'], r['proof']))
    prov = {}
    for d in sorted(glob.glob(f'{A}/la_*/')):
        name = d.split('/')[-2]
        if not glob.glob(d + 'mix_*.jsonl'): continue
        found = set()
        src = d + ('found_union_8.jsonl' if os.path.exists(d + 'found_union_8.jsonl') else 'found_8.jsonl')
        for l in open(src):
            x = json.loads(l); found.add((x['prompt'], x['proof']))
        rel = set()
        for fn in glob.glob(d + 'relabelled_*.jsonl'):
            for l in open(fn):
                x = json.loads(l); rel.add((x['prompt'], x['proof']))
        inj = set()
        if os.path.exists(d + 'inject_records.jsonl'):
            for l in open(d + 'inject_records.jsonl'):
                x = json.loads(l); inj.add((x['prompt'], x['proof']))
        c = collections.Counter(); other_len = collections.Counter(); seen = set(); nver = nbad = 0
        for fn in sorted(glob.glob(d + 'mix_*.jsonl')):
            for l in open(fn):
                x = json.loads(l); k = (x['prompt'], x['proof'])
                if k in seen: continue
                seen.add(k)
                if k in found: c['target_found'] += 1
                elif k in train_set: c['stage1_train'] += 1; other_len[rv_nlines(x['proof'])] += 1
                elif k in rel: c['relabelled'] += 1
                elif k in inj: c['injected'] += 1; other_len[rv_nlines(x['proof'])] += 1
                else:
                    c['UNKNOWN'] += 1
                    if x['prompt'] in tgt_prompts: c['UNKNOWN_target_prompt'] += 1
                if k not in train_set:
                    ok, _, _ = verify_text(x['prompt'] + ' ' + x['proof']); nver += 1; nbad += (not ok)
        prov[name] = {'provenance': dict(c), 'supervised_len_max': max(other_len), 'verified_nontrain': nver, 'rejected': nbad,
                      'relabelled_n': len(rel), 'relabelled_minlines': min((rv_nlines(p) for _, p in rel), default=None), 'injected_n': len(inj),
                      'injected_maxlines': max((rv_nlines(p) for _, p in inj), default=None)}
        print(name, prov[name], flush=True)
    json.dump(prov, open('review_out/mix_provenance.json', 'w'), indent=1)

if __name__ == '__main__':
    main()

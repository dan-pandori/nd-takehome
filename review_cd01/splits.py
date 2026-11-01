#!/usr/bin/env python3
"""Reviewer (coe-dose01): split disjointness by renaming class, own keys (common.class_key: premise-order-invariant;
class_key_set: premises as a set), between every training file of the new ladders and every evaluation pool.
Training: K12^0.1% (pretraining + replay), K12- (knockout s1 replay), RL targets, every fine-tune mix (each mix record must
be an RL-target prompt or a record of the arm's own pretraining set; then the distinct prompts are keyed).
Evaluation pools: transfer_track832, heldout1000, read1054 (incl. textbook72), p2 held-out 5,000.
Prints counts only (no statement is printed)."""
import collections, glob, gzip, hashlib, json, sys
sys.path.insert(0, '/home/dan/work/coe-dose01/review_cd01')
from common import BIG, REPO, jl, seq_of_prompt, class_key, class_key_set

COE = '/home/dan/work/create-or-elicit/data/coe'


def keys(prompts):
    k1, k2 = {}, {}
    for p in prompts:
        pr, c = seq_of_prompt(p)
        k1[p] = class_key(pr, c)
        k2[p] = class_key_set(pr, c)
    return k1, k2


def md5_of_gz(fn):
    h = hashlib.md5()
    with gzip.open(fn, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def main():
    out = {}
    evals = {'transfer_track832': f'{REPO}/data/coe/transfer_track832.jsonl', 'heldout1000': f'{REPO}/data/coe/heldout1000.jsonl',
             'read1054': f'{REPO}/data/coe/read1054.jsonl', 'p2_heldout5000': f'{REPO}/data/p2/heldout.jsonl'}
    ev_prompts = {n: [x['prompt'] for x in jl(f)] for n, f in evals.items()}
    tb72 = [x['prompt'] for x in jl(evals['read1054']) if x['name'].startswith('textbook_')]
    ev_prompts['textbook72_in_read1054'] = tb72
    ev_keys = {n: keys(set(v)) for n, v in ev_prompts.items()}
    out['eval_sizes'] = {n: len(v) for n, v in ev_prompts.items()}
    trains = {'K12_dose01': f'{COE}/train_k12dose01.jsonl.gz', 'K12_ko': f'{COE}/train_k12ko.jsonl.gz', 'rl_targets': f'{REPO}/data/ladder/rl_targets.jsonl'}
    tr_prompts = {}
    for n, f in trains.items():
        tr_prompts[n] = [x['prompt'] for x in jl(f)]
    out['train_sizes'] = {n: len(v) for n, v in tr_prompts.items()}
    out['md5_k12dose01_uncompressed'] = md5_of_gz(trains['K12_dose01'])
    # mixes: membership
    allowed = {'dose01': set(tr_prompts['K12_dose01']) | set(tr_prompts['rl_targets']), 'ko': set(tr_prompts['K12_ko']) | set(tr_prompts['rl_targets'])}
    mix_prompts = collections.defaultdict(set)
    mix_stats = {}
    for fn in sorted(glob.glob(f'{BIG}/mix/*.jsonl.gz')):
        arm = 'ko' if 'ko_s1' in fn else 'dose01'
        n = bad = 0
        for x in jl(fn):
            n += 1
            mix_prompts[arm].add(x['prompt'])
            if x['prompt'] not in allowed[arm]:
                bad += 1
        mix_stats[fn.split('/')[-1]] = (n, bad)
    out['mix_records_outside_targets_or_own_pretraining'] = {k: v[1] for k, v in mix_stats.items()}
    out['mix_records'] = {k: v[0] for k, v in mix_stats.items()}
    for arm, ps in mix_prompts.items():
        tr_prompts[f'mix_union_{arm}'] = sorted(ps)
    res = {}
    for tn, tp in tr_prompts.items():
        k1, k2 = keys(set(tp))
        s1, s2 = set(k1.values()), set(k2.values())
        for en, (e1, e2) in ev_keys.items():
            res[f'{tn} x {en}'] = dict(order_invariant=len(s1 & set(e1.values())), set_key=len(s2 & set(e2.values())),
                                       literal_prompt=len(set(tp) & set(ev_prompts[en])))
        print(tn, {en: res[f'{tn} x {en}'] for en in ev_keys}, flush=True)
    out['overlaps'] = res
    # dose set vs K12- / K12: how many records differ (sigma records added)
    json.dump(out, open(f'{REPO}/review_cd01/out/splits.json', 'w'), indent=1)
    print('mix records outside targets / own pretraining set:', sum(out['mix_records_outside_targets_or_own_pretraining'].values()),
          'of', sum(out['mix_records'].values()), 'in', len(mix_stats), 'mix files')
    print('md5 of uncompressed K12^0.1%:', out['md5_k12dose01_uncompressed'])


if __name__ == '__main__':
    main()

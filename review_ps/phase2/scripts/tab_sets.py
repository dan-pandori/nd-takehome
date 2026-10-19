"""Per-set recount for TABLES.md sections 1-4, 6-8, 10, 12 from the REVIEWER's per-record label and theorem files.
Streams one label file at a time (memory-light). Writes tab_sets.out.json. Prints no theorem/proof text."""
import collections
import gzip
import json

O = '/home/dan/review/proof-strategies/review_ps/out'
D = '/home/dan/review/proof-strategies/data/ps'
OUT = '/home/dan/review/proof-strategies/phase2/scripts/tab_sets.out.json'
STRATS = ['direct', 'and_intro', 'cond_proof', 'or_intro', 'cases', 'disj_syll', 'neg_intro', 'mod_tollens', 'ex_falso',
          'contradiction', 'dne', 'lem', 'lemma_reuse']
PRIM_OK = set(STRATS) - {'lemma_reuse'} | {'trivial'}
KINDS = ('vacuous', 'pointless', 'scaffolded', 'neg_goal', 'free')
# (reviewer label file, reviewer theorem file or None)
SETS = [('k12', 'k12'), ('cap6', 'cap6'), ('k12ko', 'k12ko'), ('k12dose1', 'k12dose1'),
        ('rl_targets_gen', 'rl_targets'), ('transfer_gen', 'transfer'), ('holdout250_gen', 'holdout250'),
        ('k12_min990', 'k12_min990'), ('tb_schema_search', 'tb_schema'), ('charles_base', 'charles_base'),
        ('textbook72_search', 'textbook72')]
LBINS = [('2-4', 2, 4), ('5-8', 5, 8), ('9-12', 9, 12), ('13+', 13, 10 ** 9)]
DBINS = [('0', 0, 0), ('1', 1, 1), ('2', 2, 2), ('3+', 3, 10 ** 9)]

# K12 sample indices for s5 (uses vs requires) and s8 (like for like)
pod990 = [json.loads(l) for l in open(f'{D}/pod/k12_min990.jsonl')]
pod594 = [json.loads(l) for l in open(f'{D}/pod/k12_nec594.jsonl')]
want_k12 = {r['k12_index'] for r in pod990} | {r['k12_index'] for r in pod594}


def thm_arrays(name):
    T = {}
    for l in gzip.open(f'{O}/thm_{name}.jsonl.gz', 'rt'):
        t = json.loads(l)
        T[t['i']] = (bool(t['co']), bool(t['sc_sem']), bool(t['sc_syn']), bool(t['dneg_sem']), bool(t['dneg_syn']), bool(t['inc']))
    return T


res = {}
for lab, thm in SETS:
    T = thm_arrays(thm)
    tot = dict(n_thm=len(T), co=sum(v[0] for v in T.values()), sc_sem=sum(v[1] for v in T.values()), sc_syn=sum(v[2] for v in T.values()),
               dneg_sem=sum(v[3] for v in T.values()), dneg_syn=sum(v[4] for v in T.values()), inc=sum(v[5] for v in T.values()))
    n = 0
    uses = collections.Counter(); sub = collections.Counter(); prim = collections.Counter(); cur = collections.Counter()
    boxfree = 0; no_strat = 0; unlab = 0; w_only = 0; dead = 0; sum_kept = 0; sum_lines = 0
    R = 0; kc = collections.Counter(); wk = 0; nonwork_template = 0; nonwork_not_template = 0; kind_none = 0
    xt = collections.Counter()
    lb = {b: collections.Counter() for b, _, _ in LBINS}; db = {b: collections.Counter() for b, _, _ in DBINS}
    bylen = collections.defaultdict(collections.Counter); bydep = collections.defaultdict(collections.Counter)
    keep = {}
    for l in gzip.open(f'{O}/labels_{lab}.jsonl.gz', 'rt'):
        a = json.loads(l)
        if 'skip' in a:
            continue
        n += 1
        u = set(a['uses']); s = set(a['sub'])
        uses.update(u); sub.update(s); prim[a['primary']] += 1; cur[a['curried']] += 1
        boxfree += bool(a['boxfree']); no_strat += (len(u) == 0); unlab += (a['primary'] not in PRIM_OK)
        w_only += bool(set(a['w_uses']) - u); dead += (a['n_lines'] != a['n_kept'])
        sum_kept += a['n_kept']; sum_lines += a['n_lines']
        if 'contradiction' in u:
            R += 1
            for k in KINDS:
                kc[k] += (f'contradiction.{k}' in s)
            if 'contradiction.working' in s:
                wk += 1
            elif 'contradiction.template' in s:
                nonwork_template += 1
            else:
                nonwork_not_template += 1
            if not any(f'contradiction.{k}' in s for k in KINDS):
                kind_none += 1
        # theorem cross-tab
        co, scs, scy, dns, dny, inc = T[a['i']]
        cw = 'contradiction.working' in s
        xt['pairs'] += 1
        if 'contradiction' in u:
            xt['ru'] += 1; xt['ru_co'] += co
        if co:
            xt['co'] += 1; xt['co_red'] += ('contradiction' in u)
            xt['co_dne_only'] += ('dne' in u and 'contradiction' not in u)
            xt['co_neither'] += ('dne' not in u and 'contradiction' not in u)
            xt['co_lem_only'] += ('lem' in u and 'dne' not in u and 'contradiction' not in u)
        if scs:
            xt['sc_sem'] += 1; xt['sc_sem_cw'] += cw; xt['sc_sem_cw_or_lem'] += (cw or 'lem' in u); xt['sc_sem_lem'] += ('lem' in u)
        if scy:
            xt['sc_syn'] += 1; xt['sc_syn_cw'] += cw; xt['sc_syn_cw_or_lem'] += (cw or 'lem' in u)
        xt['inc'] += inc; xt['inc_exf_incprem'] += (inc and 'ex_falso.inconsistent_premises' in s)
        xt['exf_incprem'] += ('ex_falso.inconsistent_premises' in s)
        xt['exf_incprem_not_inc'] += ('ex_falso.inconsistent_premises' in s and not inc)
        # bins (pruned length, pruned depth)
        flags = {'w_red': cw, 'w_negi': 'neg_intro.working' in s, 'gen_ore': 'cases.genuine' in s,
                 'mt': 'mod_tollens' in u, 'ds': 'disj_syll' in u}
        for b, lo, hi in LBINS:
            if lo <= a['n_kept'] <= hi:
                lb[b]['n'] += 1; lb[b].update({k: 1 for k, v in flags.items() if v})
        for b, lo, hi in DBINS:
            if lo <= a['depth'] <= hi:
                db[b]['n'] += 1; db[b].update({k: 1 for k, v in flags.items() if v})
        bylen[str(a['n_kept'])]['n'] += 1; bylen[str(a['n_kept'])].update(u)
        bydep[str(a['depth'])]['n'] += 1; bydep[str(a['depth'])].update(u)
        if lab == 'k12' and a['i'] in want_k12:
            keep[a['i']] = {'uses': sorted(u), 'sub': sorted(s), 'n_kept': a['n_kept']}
        if lab == 'k12_min990':
            keep[a['i']] = {'uses': sorted(u), 'sub': sorted(s), 'n_kept': a['n_kept']}
    res[lab] = dict(n=n, uses=dict(uses), sub=dict(sub), primary=dict(prim), curried=dict(cur), boxfree=boxfree, no_strategy=no_strat,
                    unlabelled=unlab, strategy_only_dead=w_only, records_with_dead_lines=dead, mean_kept=sum_kept / n, mean_lines=sum_lines / n,
                    reductio=dict(R=R, kinds=dict(kc), any_working=wk, nonworking_with_template=nonwork_template,
                                  nonworking_without_template=nonwork_not_template, no_kind=kind_none),
                    thm_totals=tot, xtab=dict(xt), lbins={b: dict(c) for b, c in lb.items()}, dbins={b: dict(c) for b, c in db.items()},
                    bylen={k: dict(v) for k, v in bylen.items()}, bydep={k: dict(v) for k, v in bydep.items()})
    if keep:
        res[lab]['keep'] = {str(k): v for k, v in keep.items()}
    print(lab, n, 'R', R, dict(kc), 'wk', wk, 'xt', dict(xt), flush=True)
    del T
json.dump(res, open(OUT, 'w'))
print('written', OUT)

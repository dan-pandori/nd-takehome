"""T1 ladders: recount found_transfer_8 / found_8 and round_8, match every counted ND proof to an accepted literal
text in the ladder's LEAN_GATE_DUMP, and draw a Lean re-check sample. One dump downloaded at a time, then deleted."""
import json, os, sys, random, subprocess, collections
sys.path.insert(0, os.path.dirname(__file__))
from rv_common import rd, term_size, n_haves

B = os.path.expanduser(os.environ.get('RV_BASE', '~/review/state-cap12'))
A = f'{B}/artifacts/sc12'
orig = {r['prompt']: r for r in rd(f'{B}/data/ladder/transfer.jsonl')}
tg = {r['prompt']: r for r in rd(f'{B}/data/ladder/rl_targets.jsonl')}
rng = random.Random(99)
res = json.load(open(f'{B}/rv/ladder_recount.json')) if os.path.exists(f'{B}/rv/ladder_recount.json') else {}
samp = []
for name in sys.argv[1:]:
    ft = list(rd(f'{A}/{name}/found_transfer_8.jsonl'))
    fo = list(rd(f'{A}/{name}/found_8.jsonl'))
    r8 = json.load(open(f'{A}/{name}/round_8.json'))
    solved_t = {x['prompt'] for x in ft}; solved_g = {x['prompt'] for x in fo}
    gz = f'{B}/dl/{name}.jsonl.gz'
    subprocess.run(['hf', 'buckets', 'cp', f'hf://buckets/dan-pandori/nd-rl/state-cap12/artifacts/sc12/dump/{name}.jsonl.gz', gz],
                   check=True, capture_output=True)
    acc = collections.defaultdict(dict)       # prompt -> nd -> text
    for r in rd(gz):
        if r['lean_ok'] is True:
            acc[r['prompt']].setdefault(r['nd'], r['lean_text'])
    os.unlink(gz)
    def match(recs):
        m = miss = 0
        for x in recs:
            if x['proof'] in acc.get(x['prompt'], {}):
                m += 1
            else:
                miss += 1
        return m, miss
    mt, mst = match(ft); mg, msg = match(fo)
    dump_t = {p for p in acc if p in orig}
    lt = lambda p: int(orig[p]['L_true'])
    bins = collections.Counter(lt(p) for p in solved_t)
    ge = {L: sum(1 for p in solved_t if lt(p) >= L) for L in range(2, 21)}
    lstar5 = max([L for L, c in ge.items() if c >= 5], default=0)
    # shortest literal text per solved transfer theorem (among counted proofs)
    ts = collections.defaultdict(list)
    for p in solved_t:
        texts = [acc[p][x['proof']] for x in ft if x['prompt'] == p and x['proof'] in acc.get(p, {})]
        if texts:
            ts[lt(p)].append(min(term_size(t) for t in texts))
    res[name] = dict(transfer_solved=len(solved_t), transfer_n=len(orig), targets_solved=len(solved_g),
                     exec_round8_transfer_cum=r8['transfer_cum']['solved'], exec_round8_targets_cum=r8['targets_cum']['solved'],
                     exec_lstar_transfer=r8['transfer_cum']['lstar'], exec_lstar_targets=r8['targets_cum']['lstar'],
                     lstar5_transfer=lstar5, max_L_transfer=max(bins) if bins else None,
                     n_ge13_transfer=sum(v for L, v in bins.items() if L >= 13), bins_transfer=dict(sorted(bins.items())),
                     counted_transfer_proofs=len(ft), matched_transfer=mt, unmatched_transfer=mst,
                     counted_target_proofs=len(fo), matched_targets=mg, unmatched_targets=msg,
                     dump_only_transfer=len(dump_t - solved_t), found_not_in_dump=len(solved_t - dump_t),
                     termsize_med_by_L={L: sorted(v)[len(v) // 2] for L, v in sorted(ts.items())},
                     heldout_greedy_r8=r8.get('heldout_greedy', {}).get('rate'))
    print(name, res[name], flush=True)
    for pool, recs in (('transfer', ft), ('targets', fo)):
        ok = [x for x in recs if x['proof'] in acc.get(x['prompt'], {})]
        byp = collections.defaultdict(list)
        for x in ok:
            byp[x['prompt']].append(x)
        ps = sorted(byp); rng.shuffle(ps)
        for p in ps[:110 if pool == 'transfer' else 60]:
            x = rng.choice(byp[p])
            samp.append({'tag': f'{name}:{pool}', 'prompt': p, 'text': acc[p][x['proof']], 'expect': True})
    json.dump(res, open(f'{B}/rv/ladder_recount.json', 'w'), indent=1)
    with open(f'{B}/rv/lean_sample_ladder.jsonl', 'a') as f:
        for s in samp:
            f.write(json.dumps(s, ensure_ascii=False) + '\n')
    samp = []

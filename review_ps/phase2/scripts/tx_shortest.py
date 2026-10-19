#!/usr/bin/env python3
"""Phase-2 sub-audit (examples): re-derive the selection of every canonical K12 example from the labels, with an own
re-implementation of examples.py's `readable` rule and the reviewer's textbook72 class keys (never printed: indices only).
  A. shortest clean: min pruned length among CLEAN & readable K12 records, and whether shorter ones were skipped as sealed.
  B. typical: median_low pruned length of the TYPICAL pool.
  C. #10 kinds: shortest proof with only that kind, overall / readable / primary-with-kind.
  D. pool shares behind the "Typical of K12: ..." glosses.
Streams three gz files in lockstep (executor labels = reviewer labels per record, see §R2; K12 data; reviewer thm labels).
"""
import collections
import gzip
import json
import statistics
import sys

sys.path.insert(0, "/home/dan/review/proof-strategies/review_ps")
from nd import parse_prompt  # noqa: E402
from sealkey import TB72  # noqa: E402

W = "/home/dan/work/proof-strategies"
R = "/home/dan/review/proof-strategies"
STRATS = ('direct', 'and_intro', 'cond_proof', 'or_intro', 'cases', 'disj_syll', 'neg_intro', 'mod_tollens',
          'ex_falso', 'contradiction', 'dne', 'lem', 'lemma_reuse')
BASIC = {'direct', 'and_intro', 'or_intro'}
CLEAN = {
    'direct': lambda a: a['pri'] == 'direct' and a['box_free'] and set(a['u']) <= {'direct'},
    'and_intro': lambda a: a['pri'] == 'and_intro' and set(a['u']) <= BASIC,
    'cond_proof': lambda a: a['pri'] == 'cond_proof' and 'cond_proof.working' in a['psub'] and 'cond_proof.vacuous' not in a['sub'] and set(a['u']) <= BASIC | {'cond_proof'},
    'or_intro': lambda a: a['pri'] == 'or_intro' and set(a['u']) <= BASIC,
    'cases': lambda a: a['pri'] == 'cases' and 'cases.genuine' in a['psub'] and 'cases.trivial_merge' not in a['sub'] and 'cases.redundant' not in a['sub'] and set(a['u']) <= BASIC | {'cases'},
    'disj_syll': lambda a: a['pri'] == 'disj_syll' and set(a['u']) <= BASIC | {'cases', 'disj_syll', 'ex_falso'} and 'ex_falso.inconsistent_premises' not in a['sub']
                           and 'cases.genuine' in a['psub'] and not {'cases.redundant', 'cases.or_intro_decoration'} & set(a['sub']),
    'neg_intro': lambda a: a['pri'] == 'neg_intro' and 'neg_intro.working' in a['psub'] and 'neg_intro.mt' not in a['psub'] and 'neg_intro.immediate' not in a['psub'] and set(a['u']) <= BASIC | {'neg_intro'},
    'mod_tollens': lambda a: a['pri'] == 'mod_tollens' and 'mod_tollens.strict' in a['psub'] and 'mod_tollens.contraposition' not in a['psub'],
    'ex_falso': lambda a: a['pri'] == 'ex_falso' and set(a['u']) <= {'ex_falso', 'direct'},
    'contradiction': lambda a: 'contradiction.free' in a['sub'] and 'contradiction.working' in a['sub'] and 'contradiction.template' not in a['sub'],
    'dne': lambda a: a['pri'] == 'dne' and 'dne.on_premise' in a['psub'],
    'lem': lambda a: 'lem' in a['u'] and not {'cases.redundant', 'cond_proof.vacuous', 'contradiction.template'} & set(a['sub']),
    'lemma_reuse': lambda a: 'lemma_reuse' in a['u'] and 'lemma_reuse.multi_step' in a['sub'] and not set(a['u']) & {'contradiction', 'dne', 'ex_falso'} and 'cases.redundant' not in a['sub'] and 'cond_proof.vacuous' not in a['sub'],
}
TYPICAL = lambda s, a: ('lemma_reuse' in a['u']) if s == 'lemma_reuse' else a['pri'] == s  # noqa: E731
KINDS = ('vacuous', 'pointless', 'scaffolded', 'neg_goal', 'free')


def lines_of(proof):
    out = []
    for part in proof.split(";"):
        t = part.split()
        if not t or t[0] == "QED":
            continue
        k = int(t[0][1:])
        i = 1
        d = 0
        while t[i] == "|":
            i += 1
            d += 1
        c = t.index(":", i)
        out.append({"k": k, "d": d, "f": " ".join(t[i:c]), "rule": t[c + 1], "refs": [int(x[1:]) for x in t[c + 2:]]})
    return out


def readable(prompt, proof):
    if ' F ' in prompt.replace('(', ' ').replace(')', ' '):
        return False
    toks = prompt.split()
    for k in range(len(toks) - 2):
        if toks[k] in 'PQRS' and toks[k + 1] in ('&', 'v', '>') and toks[k + 2] == toks[k]:
            return False
    for ln in lines_of(proof):
        if ln['rule'] == 'AS' and ln['f'] == 'F':
            return False
        if ln['rule'] == 'R' or (len(ln['refs']) >= 2 and len(set(ln['refs'][:2])) < 2 and ln['rule'] in ('ANDI', 'NEGE')):
            return False
        if ln['rule'] in ('IMPI', 'NEGI') and ln['refs'][0] == ln['refs'][1]:
            return False
        if ln['rule'] == 'ORE' and (ln['refs'][1] == ln['refs'][2] and ln['refs'][3] == ln['refs'][4]):
            return False
    return True


def seq_size(prompt):
    return sum(1 for t in prompt.split() if t not in ('(', ')', ',', 'THM', 'SEQ', 'PRF'))


EX = json.load(open(f"{W}/artifacts/ps/examples.json"))["examples"]
clean_c = collections.defaultdict(list)      # st -> [(key, i)]
typ_lp = collections.defaultdict(list)       # st -> [(Lp, i)]
kind_c = collections.defaultdict(list)       # kd -> [(primary_with_kind, Lp, ts, i, readable)]
prompts = {}
D = collections.Counter()
nrec = 0
fa = gzip.open(f"{W}/artifacts/ps/labels/k12.jsonl.gz", "rt")
fs = gzip.open(f"{R}/data/ps/in/train_k12.jsonl.gz", "rt")
ft = gzip.open(f"{R}/review_ps/out/thm_k12.jsonl.gz", "rt")
for la, ls, lt in zip(fa, fs, ft):
    a, s, t = json.loads(la), json.loads(ls), json.loads(lt)
    assert a['i'] == t['i'] == nrec
    nrec += 1
    prompt, proof = s['prompt'], s['proof']
    rd = None
    for st in STRATS:
        if CLEAN[st](a):
            if rd is None:
                rd = readable(prompt, proof)
            if rd:
                clean_c[st].append(((a['Lp'], seq_size(prompt), a['ts'], len(a['u']), a['i']), a['i']))
                prompts[a['i']] = prompt
        if TYPICAL(st, a):
            typ_lp[st].append((a['Lp'], a['i']))
    ks = [k for k in KINDS if f'contradiction.{k}' in a['sub']]
    if len(ks) == 1:
        if rd is None:
            rd = readable(prompt, proof)
        prim = a['pri'] == 'contradiction' and f'contradiction.{ks[0]}' in a['psub']
        kind_c[ks[0]].append((prim, a['Lp'], a['ts'], a['i'], rd))
        prompts[a['i']] = prompt
    # D. pools behind the "Typical of K12" glosses
    pri = a['pri']
    if pri == 'cond_proof':
        D['cp.n'] += 1
        nimpi = sum(1 for x in lines_of(proof) if x['rule'] == 'IMPI')
        allvac = 'cond_proof.vacuous' in a['sub'] and 'cond_proof.working' not in a['sub']
        D['cp.root_vacuous'] += 'cond_proof.vacuous' in a['psub']
        D['cp.all_impi_vacuous'] += allvac
        D['cp.all_vacuous_and_2plus_impi'] += allvac and nimpi >= 2
        D['cp.Lp7'] += a['Lp'] == 7
        D['cp.Lp7.all_vacuous_and_2plus_impi'] += a['Lp'] == 7 and allvac and nimpi >= 2
    if pri == 'cases':
        D['ca.n'] += 1
        L = {x['k']: x for x in lines_of(proof)}
        root = L[max(L)]
        j = root['refs'][0]
        while L[j]['rule'] == 'R':
            j = L[j]['refs'][0]
        bote_disj = L[j]['rule'] == 'BOTE'
        red = 'cases.redundant' in a['psub']
        D['ca.inc'] += t['inc']
        D['ca.root_redundant'] += red
        D['ca.split_on_BOTE_line'] += bote_disj
        D['ca.inc&red&bote'] += t['inc'] and red and bote_disj
        # both branches ignore their case (root ORE): neither branch's case assumption reaches its end? (label-free proxy
        # not available; reported only for the example via the gloss audit)
    if pri == 'neg_intro':
        D['ni.n'] += 1
        D['ni.root_vacuous'] += 'neg_intro.vacuous' in a['psub']
        D['ni.inc'] += t['inc']
        D['ni.root_vacuous&inc'] += 'neg_intro.vacuous' in a['psub'] and t['inc']
    if pri == 'contradiction':
        D['co.n'] += 1
        for k in KINDS:
            D[f'co.root_kind.{k}'] += f'contradiction.{k}' in a['psub']
        if 'contradiction.scaffolded' in a['psub']:
            body = prompt[4:-4]
            prem, concl = body.split(' SEQ ')
            G = concl.strip()
            D['co.scaff.prem_has_notG_imp_F'] += ('( ( ~ ' + G + ' ) > F )') in prem
            D['co.scaff.prem_has_notnotG'] += ('( ~ ( ~ ' + G + ' ) )') in prem
    if 'contradiction' in a['u']:
        D['c10.users'] += 1
        for k in KINDS:
            D[f'c10.users_with_kind.{k}'] += f'contradiction.{k}' in a['sub']
for f in (fa, fs, ft):
    f.close()
print("records:", nrec)

tb = TB72(path=f"{R}/data/bs/textbook72.jsonl")


def sealed_keys(i):
    p, c = parse_prompt(prompts[i])
    return sorted(tb.hits(p, c))


exi = {(e['strategy'], e['role'].split(' (')[0]): e for e in EX}
out = {"shortest": {}, "typical": {}, "kinds": {}, "pools": dict(D)}
print("\nA. shortest clean (K12, CLEAN & readable): example Lp | min Lp | #at min | first in key order (sealed?) | "
      "first unsealed | example idx")
for st in STRATS:
    c = sorted(clean_c[st])
    e = exi.get((st, 'shortest clean'))
    if not c:
        print(f"  {st}: no K12 clean readable candidate; example from {e['source'] if e else None}")
        out["shortest"][st] = {"k12_candidates": 0}
        continue
    mn = c[0][0][0]
    at = [i for k, i in c if k[0] == mn]
    seal_first = []
    first_unsealed = None
    for k, i in c:
        h = sealed_keys(i)
        if h:
            seal_first.append((i, k[0], h))
            continue
        first_unsealed = (i, k[0])
        break
    print(f"  {st}: ex Lp {e['labels']['Lp']} | min {mn} | n at min {len(at)} (total clean readable {len(c)}) | "
          f"skipped as sealed before first unsealed: {[(i, lp, h) for i, lp, h in seal_first]} | first unsealed {first_unsealed} | ex {e['index']}")
    out["shortest"][st] = {"ex_Lp": e['labels']['Lp'], "min_Lp": mn, "n_at_min": len(at), "n_clean_readable": len(c),
                           "sealed_skipped": seal_first, "first_unsealed": first_unsealed, "ex_index": e['index']}
print("\nB. typical: median_low of the pool (pool minus the chosen shortest-clean K12 record)")
for st in STRATS:
    e = exi.get((st, 'typical'))
    ch = exi.get((st, 'shortest clean'))
    chosen = {ch['index']} if ch and ch['source'] == 'K12' else set()
    grp = [lp for lp, i in typ_lp[st] if i not in chosen or len(typ_lp[st]) == 1]
    med = statistics.median_low(grp) if grp else None
    print(f"  {st}: pool {len(grp)} median_low {med} | example {e['labels']['Lp'] if e else None} (idx {e['index'] if e else None})")
    out["typical"][st] = {"pool": len(grp), "median_low": med, "ex_Lp": e['labels']['Lp'] if e else None}
print("\nC. #10 kinds (records with exactly one kind)")
for kd in KINDS:
    c = kind_c[kd]
    e = exi[('contradiction', f'kind {kd}')]
    allmin = min(x[1] for x in c)
    rmin = min((x[1] for x in c if x[4]), default=None)
    pmin = min((x[1] for x in c if x[0]), default=None)
    prmin = min((x[1] for x in c if x[0] and x[4]), default=None)
    nprim = sum(1 for x in c if x[0])
    nprim_read = sum(1 for x in c if x[0] and x[4])
    shorter_nonread = sorted({(x[3], x[1], x[0]) for x in c if x[1] < e['labels']['Lp']})[:8]
    print(f"  {kd}: n {len(c)} | min Lp all {allmin}, readable {rmin}, primary {pmin} (n {nprim}), readable primary {prmin} "
          f"(n {nprim_read}) | example idx {e['index']} Lp {e['labels']['Lp']} pri {e['labels']['pri']} | "
          f"records shorter than the example (idx, Lp, primary-with-kind): {shorter_nonread}")
    out["kinds"][kd] = {"n": len(c), "min_all": allmin, "min_readable": rmin, "min_primary": pmin, "n_primary": nprim,
                        "min_readable_primary": prmin, "n_readable_primary": nprim_read, "ex_index": e['index'],
                        "ex_Lp": e['labels']['Lp'], "ex_pri": e['labels']['pri'], "shorter": shorter_nonread}
print("\nD. pools:")
for k in sorted(D):
    print("  ", k, D[k])
json.dump(out, open(f"{R}/phase2/scripts/tx_shortest.out.json", "w"), indent=1)

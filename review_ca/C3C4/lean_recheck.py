"""Own Lean re-check of counted proofs + negative controls for C3 and C4. Reject on ANY error (or sorry)."""
import json, random, sys, collections, statistics
from common import *
sys.path.insert(0, ROOT)
import nd2lean   # FORMAT CONVERSION ONLY (ND -> Lean body) for textbook72-run cells, which stored no literal text
rng = random.Random(0)
TBP = {r['prompt'] for f in ('textbook_dev', 'textbook_train') for r in jl(ROOT + '/data/eval_only/textbook72/%s.jsonl' % f)}
rr = {r['prompt']: r for r in jl(ROOT + '/data/ladder/transfer_long_rr600.jsonl')}
Q = {p for p, r in rr.items() if r['source'] == 'gen' and 13 <= r['L_true'] <= 16}
SC = RAW + '/state-cap12/artifacts/sc12/dump/'
items = []   # (claim, arm, prompt, src, body, kind, tsize, ndlines)
def one_line(prompt, text): return statement(prompt) + ' ' + text
def from_dump(claim, arm, fn, P):
    acc = collections.defaultdict(list)
    for d in jl(fn):
        if d['prompt'] in P and truthy(d['lean_ok']): acc[d['prompt']].append((d['lean_text'], d['nd']))
    for p in sorted(acc):
        t, nd = rng.choice(acc[p])
        items.append(dict(claim=claim, arm=arm, prompt=p, src=one_line(p, t), text=t, kind='literal', ts=term_size(t), nl=nd_lines(nd)))
C3 = {'SN12_T1_s0': SC + 'rr_T1_SN12_s0__rr600.jsonl.gz', 'SN12_T1_s1': MY + '/rr_T1_SN12_s1__rr600.jsonl.gz',
      'SN12_T1_s2': MY + '/rr_T1_SN12_s2__rr600.jsonl.gz', 'SN12_T1_s3': MY + '/rr_T1_SN12_s3__rr600.jsonl.gz',
      'K12_T1_s0': SC + 'rr_T1_K12_s0__rr600.jsonl.gz', 'K12_T1_s1': MY + '/rr_T1_K12_s1__rr600.jsonl.gz'}
for a, fn in C3.items(): from_dump('C3', a, fn, Q)
BS = RAW + '/best-state/artifacts/bs/dump/'
for a in ('Fz', 'T1'):
    for c in ('best6', 'best12'):
        for s in range(3):
            lab = '%s_%s_s%d' % (a, c, s); from_dump('C4', lab, BS + lab + '__tb72.jsonl.gz', TBP)
T72 = RAW + '/textbook72/artifacts/textbook72/eval/'
import os
for lab in ['Fz_SN6_s0', 'Fz_SN6_s1', 'T1_SN6_s0', 'T1_SN6_s1'] + ['%s_SN12_s%d' % (a, s) for a in ('Fz', 'T1') for s in range(4)]:
    fn = T72 + lab + '.jsonl'
    if not os.path.exists(fn): fn = MY + '/tb/' + lab + '.jsonl'
    for d in jl(fn):
        if d['prompt'] in TBP and truthy(d['solved']) and d.get('proofs'):
            nd = rng.choice(d['proofs'])
            try:
                s = nd2lean.translate(d['prompt'], nd, require_all_pr=False)
            except Exception as e:
                items.append(dict(claim='C4', arm=lab, prompt=d['prompt'], src=None, text='', kind='nd2lean-fail', ts=0, nl=nd_lines(nd))); continue
            body = s.split(':= by\n', 1)[1]
            items.append(dict(claim='C4', arm=lab, prompt=d['prompt'], src=statement(d['prompt']) + '\n' + body, text=body, kind='nd2lean', ts=term_size(body.replace('\n', ' ')), nl=nd_lines(nd)))
print('positives', collections.Counter((i['claim'], i['kind']) for i in items))
# ---- negative controls ----
def segs(text):
    out, cur, d = [], [], 0
    for t in text.split():
        if t in ('(', '⟨'): d += 1
        if t in (')', '⟩'): d -= 1
        if t == ';' and d == 0: out.append(cur); cur = []
        else: cur.append(t)
    out.append(cur); return out
neg = []
for claim in ('C3', 'C4'):
    lit = [i for i in items if i['claim'] == claim and i['kind'] == 'literal']
    sample = rng.sample(lit, min(100, len(lit)))
    for i in sample:
        S = segs(i['text']); last = S[-1]
        # 1 drop the top-level have that the final `exact` returns
        if len(last) == 2 and last[0] == 'exact':
            nm = last[1]; keep = [s for s in S if not (len(s) > 1 and s[0] == 'have' and s[1] == nm)]
            if len(keep) < len(S):
                neg.append(dict(claim=claim, ctl='drop-line', src=one_line(i['prompt'], ' ; '.join(' '.join(s) for s in keep))))
        # 2 swap hypotheses h1<->h2 in the statement (only if both are cited and their formulas differ)
        prem, c = parse_prompt(i['prompt'])
        toks = i['text'].split()
        if len(prem) >= 2 and 'h1' in toks and 'h2' in toks and prem[0] != prem[1]:
            hs = ' '.join('( h%d : %s )' % (k + 1, lean_f(p)) for k, p in enumerate([prem[1], prem[0]] + prem[2:]))
            neg.append(dict(claim=claim, ctl='swap-hyp', src='theorem t ( P Q R S : Prop ) %s : %s := by %s' % (hs, lean_f(c), i['text'])))
        # 3 pair the proof with another theorem of a different conclusion
        while True:
            j = rng.choice(lit)
            if parse_prompt(j['prompt'])[1] != c: break
        neg.append(dict(claim=claim, ctl='other-theorem', src=one_line(j['prompt'], i['text'])))
        # 4 truncate the literal text at 60 % of its tokens (parse-error-recovery trap)
        tt = i['text'].split(); neg.append(dict(claim=claim, ctl='truncate-60%', src=one_line(i['prompt'], ' '.join(tt[:int(len(tt) * 0.6)]))))
print('negatives', collections.Counter((n['claim'], n['ctl']) for n in neg))
allsrc = [i['src'] for i in items if i['src']] + [n['src'] for n in neg]
res = []
B = 100
for k in range(0, len(allsrc), B):
    r, out = lean_batch(allsrc[k:k + B]); res += r
    print('batch', k // B, 'ok', sum(x[0] for x in r), '/', len(r), flush=True)
pi = 0
for i in items:
    if i['src']: i['ok'], i['msg'] = res[pi]; pi += 1
    else: i['ok'], i['msg'] = False, ['nd2lean translation failed']
for n in neg: n['ok'], n['msg'] = res[pi]; pi += 1
json.dump(dict(items=[{k: v for k, v in i.items() if k != 'src'} for i in items], neg=neg), open(ROOT + '/rv/C3C4/lean_recheck.json', 'w'))
print('\n%-14s %-8s %5s %5s %5s | term size med/max | ND lines med/max' % ('arm', 'kind', 'n', 'ok', 'rej'))
by = collections.defaultdict(list)
for i in items: by[(i['claim'], i['arm'], i['kind'])].append(i)
for (cl, a, kd), L in sorted(by.items()):
    ts = [x['ts'] for x in L]; nl = [x['nl'] for x in L]
    print('%s %-13s %-8s %5d %5d %5d | %5.0f %5d | %4.0f %4d' % (cl, a, kd, len(L), sum(x['ok'] for x in L), sum(not x['ok'] for x in L), statistics.median(ts), max(ts), statistics.median(nl), max(nl)))
for i in items:
    if not i['ok']: print('REJECTED', i['claim'], i['arm'], i['kind'], i['prompt'][:70], i['msg'][:2])
c = collections.defaultdict(lambda: [0, 0])
for n in neg: c[(n['claim'], n['ctl'])][0] += 1; c[(n['claim'], n['ctl'])][1] += (not n['ok'])
for k, (n, r) in sorted(c.items()): print('NEG', k, 'rejected %d / %d' % (r, n))

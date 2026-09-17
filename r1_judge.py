#!/usr/bin/env python3
"""run1-lean: judge model outputs. tokens/english -> nd_verify; lean -> Lean 4 (batched, VPS).

  python r1_judge.py --gen artifacts/r1/gen_coder30b.jsonl --prompts data/r1/prompts.jsonl --out artifacts/r1/judged_coder30b.jsonl [--procs 2]

Per record adds: greedy_ok, greedy_reason, sample_ok (list), sample_reason (list), extracted proofs.
Extraction: code fences stripped; tokens: from the first `N<digit>` up to and including QED (a leading
`THM … PRF` is dropped); english: numbered lines up to QED, parsed back to tokens; lean: the text after the
first `:=` that follows `theorem` (or the whole output if no `theorem`), compiled under the fixed header.
"""
import argparse, json, os, sys, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nd_verify import verify_text
import nd2lean as L

FENCE = re.compile(r'```[a-zA-Z0-9]*\n(.*?)```', re.S)


def strip_fence(t):
    m = FENCE.findall(t)
    return max(m, key=len) if m else t


def extract_tokens(t):
    t = strip_fence(t)
    toks = t.split()
    if 'PRF' in toks:
        toks = toks[toks.index('PRF') + 1:]
    start = next((i for i, x in enumerate(toks) if re.fullmatch(r'N\d+', x)), None)
    if start is None:
        return None
    toks = toks[start:]
    if 'QED' in toks:
        toks = toks[:toks.index('QED') + 1]
    else:
        toks = toks + ['QED']
    return ' '.join(toks)


def extract_english(t):
    t = strip_fence(t)
    lines = []
    for raw in t.splitlines():
        s = raw.strip()
        if re.match(r'^\d+\.', s):
            lines.append(s)
        elif s == 'QED' and lines:
            break
    if not lines:
        return None
    return L.english_to_tokens('\n'.join(lines))


def extract_lean(t):
    t = strip_fence(t)
    m = re.search(r'theorem\b', t)
    if m:
        i = t.find(':=', m.end())
        if i < 0:
            return None
        body = t[i + 2:]
    else:
        body = t
    # drop anything after a blank line followed by prose / a second declaration
    body = re.split(r'\n\s*\n(?=[^\s])', body, maxsplit=1)[0]
    body = body.strip('\n')
    if not body.strip():
        return None
    # make sure the term is indented (a fun/have chain must sit in the body position)
    return '\n'.join(('  ' + ln if ln and not ln.startswith(' ') else ln) for ln in body.splitlines()) + '\n'


def judge_nd(prompt, body):
    if body is None:
        return False, 'no proof found'
    ok, reason, nl = verify_text(prompt + ' ' + body)
    return ok, reason


def judge_nd_lenient(prompt, body):
    """Secondary metric: formula parentheses repaired (nd2lean.repair_proof) before verification."""
    if body is None:
        return False, 'no proof found'
    rb = L.repair_proof(body)
    ok, reason, nl = verify_text(prompt + ' ' + rb)
    return ok, reason


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--gen', required=True)
    ap.add_argument('--prompts', default='data/r1/prompts.jsonl')
    ap.add_argument('--out', required=True)
    ap.add_argument('--procs', type=int, default=2)
    ap.add_argument('--batch', type=int, default=40)
    a = ap.parse_args()
    meta = {}
    for l in open(a.prompts):
        p = json.loads(l)
        meta[p['id']] = (p['nd_prompt'], p['lean_header'], p['stratum'], p['src'], p['gen_lines'])
    recs = [json.loads(l) for l in open(a.gen) if l.strip()]
    lean_items, lean_slots = [], []
    for r in recs:
        nd_prompt, header, stratum, src, gl = meta[r['id']]
        r['stratum'], r['src'], r['gen_lines'] = stratum, src, gl
        outs = ([('greedy', r['greedy'])] if r.get('greedy') is not None else []) + [(f's{i}', s) for i, s in enumerate(r['samples'])]
        r['judged'] = {}
        for k, txt in outs:
            if r['form'] in ('tokens', 'english'):
                body = extract_tokens(txt) if r['form'] == 'tokens' else extract_english(txt)
                ok, reason = judge_nd(nd_prompt, body)
                okl, reasonl = judge_nd_lenient(nd_prompt, body)
                r['judged'][k] = {'ok': ok, 'reason': reason, 'proof': body, 'ok_lenient': okl, 'reason_lenient': reasonl}
            else:
                body = extract_lean(txt)
                if body is None:
                    r['judged'][k] = {'ok': False, 'reason': 'no proof found', 'proof': None, 'ok_lenient': False, 'reason_lenient': 'no proof found'}
                else:
                    r['judged'][k] = {'ok': None, 'reason': None, 'proof': body}
                    lean_items.append((header, body))
                    lean_slots.append((r, k))
    print(f'{len(recs)} records; {len(lean_items)} Lean checks', flush=True)
    if lean_items:
        import multiprocessing
        chunks = [lean_items[i:i + a.batch] for i in range(0, len(lean_items), a.batch)]
        with multiprocessing.Pool(a.procs) as pool:
            outs = pool.map(L.lean_check_many, chunks, chunksize=1)
        flat = [x for o in outs for x in o]
        for (r, k), (ok, msg) in zip(lean_slots, flat):
            r['judged'][k] = {'ok': ok, 'reason': msg if not ok else 'ok', 'proof': r['judged'][k]['proof'], 'ok_lenient': ok, 'reason_lenient': msg if not ok else 'ok'}
    for r in recs:
        j = r['judged']
        r['greedy_ok'] = j['greedy']['ok'] if 'greedy' in j else None
        r['sample_ok'] = [j[f's{i}']['ok'] for i in range(len(r['samples']))]
        r['greedy_ok_lenient'] = j['greedy']['ok_lenient'] if 'greedy' in j else None
        r['sample_ok_lenient'] = [j[f's{i}']['ok_lenient'] for i in range(len(r['samples']))]
        r['n_lines'] = {k: (verify_text(meta[r['id']][0] + ' ' + v['proof'])[2] if (v['ok'] and r['form'] != 'lean') else None) for k, v in j.items()}
    with open(a.out, 'w') as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    # summary
    agg = collections.defaultdict(lambda: [0, 0, 0, 0, 0, 0])
    for r in recs:
        g = agg[(r['model'], r['form'])]
        g[0] += 1
        g[1] += bool(r['greedy_ok'])
        g[2] += sum(r['sample_ok']) / max(1, len(r['sample_ok']))
        g[3] += any(r['sample_ok'])
        g[4] += bool(r['greedy_ok_lenient'])
        g[5] += any(r['sample_ok_lenient'])
    print('| model | form | n | greedy | pass@1 | pass@n | greedy lenient | pass@n lenient |')
    print('|---|---|---:|---:|---:|---:|---:|---:|')
    for (m, fm), (n, g, p1, pn, gl, pnl) in sorted(agg.items()):
        print(f'| {m} | {fm} | {n} | {g / n:.3f} | {p1 / n:.3f} | {pn / n:.3f} | {gl / n:.3f} | {pnl / n:.3f} |')


if __name__ == '__main__':
    main()

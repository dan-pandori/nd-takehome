"""review_coep/members.py -- member-level claims about knockout ladders (phase 2 checks of 05_results §ko-s1)."""
import json, os, sys, gzip
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
BIGE = os.path.expanduser('~/review/coep_big/eval')
S = set(strict_names())


def plain(fn):
    rows = read_rows(fn)
    return {n: r['n_ok'] for n, r in rows.items() if r['n_ok'] > 0 and n in S}


def guided(fn):
    return {r['name']: r['n_ok'] for r in jl(fn) if r['n_ok'] > 0 and r['name'] in S}


for s in (1, 2, 4, 5):
    print(f'== knockout s{s}')
    draws = {'r16 x0': f'{BIGE}/r16_ko_s{s}_x0.jsonl.gz', 'r16 x1': f'{BIGE}/r16_ko_s{s}_x1.jsonl.gz',
             'r16 C1 std': f'{EVAL}/c1_ko_s{s}_std.jsonl.gz', 'r16 C1 dbl': f'{EVAL}/c1_ko_s{s}_dbl.jsonl.gz'}
    for k, fn in draws.items():
        print(f'  {k:11s} {plain(fn)}')
    g = f'{BIGE}/r16_ko_s{s}_g0.rows.jsonl.gz'
    if os.path.exists(g):
        print(f'  r16 guided  {guided(g)}')
    if s == 1:
        for k in ('r20', 'r24'):
            print(f'  {k} x0     {plain(f"{BIGE}/{k}_ko_s1_x0.jsonl.gz")}')
cert = json.load(open(P('review_coe/out_cert.json')))['cert']
for s in ('1', '2', '4', '5'):
    ms = cert[s]['members_with_success_any_of_178']
    print(f'large-k early-stopped successes, base s{s}, strict members:', {m: v for m, v in ms.items() if m in S})

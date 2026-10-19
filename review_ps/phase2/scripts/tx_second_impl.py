#!/usr/bin/env python3
"""Phase-2 sub-audit (TAXONOMY §6 second implementation, v1.2 final): compare the second implementer's per-record output
with the REVIEWER's labels on both sets (uses, primary, and every sub-type id the second implementation emits, after
mapping route_X -> X).  Streams; counts only."""
import collections, gzip, json
W = "/home/dan/work/proof-strategies/artifacts/ps/validation"
RV = "/home/dan/review/proof-strategies/review_ps/out"
for tag, si, rv in (("tb_schema", "second_impl_v1.2final_tb_schema.jsonl.gz", "labels_tb_schema_search.jsonl.gz"),
                    ("k12", "second_impl_v1.2final_k12.jsonl.gz", "labels_k12.jsonl.gz")):
    C = collections.Counter()
    ids_seen = set()
    for ls, lr in zip(gzip.open(f"{W}/{si}", "rt"), gzip.open(f"{RV}/{rv}", "rt")):
        s, r = json.loads(ls), json.loads(lr)
        assert s['i'] == r['i']
        C['n'] += 1
        C['uses differ'] += set(s['u']) != set(r['uses'])
        C['primary differ'] += s['pri'] != r['primary']
        ssub = {x.replace('route_', '') for x in s['sub']}
        ids_seen |= {x.split('.')[0] + '.' + x.split('.')[1] for x in ssub}
        # compare only the ids the second implementation can emit (its id vocabulary, collected below in a 2nd pass)
        r_sub = set(r['sub'])
        C['_pairs'] += 0
        s_only = ssub - r_sub
        C['records with a 2nd-impl sub id the reviewer lacks'] += bool(s_only)
    print(tag, dict(C))
    # second pass: reviewer ids restricted to the 2nd-impl vocabulary
    C2 = collections.Counter()
    for ls, lr in zip(gzip.open(f"{W}/{si}", "rt"), gzip.open(f"{RV}/{rv}", "rt")):
        s, r = json.loads(ls), json.loads(lr)
        ssub = {x.replace('route_', '') for x in s['sub']}
        rsub = {x for x in r['sub'] if x in ids_seen}
        C2['records whose sub-type sets differ (2nd-impl vocabulary)'] += ssub != rsub
    print(tag, dict(C2), '| vocabulary size', len(ids_seen))

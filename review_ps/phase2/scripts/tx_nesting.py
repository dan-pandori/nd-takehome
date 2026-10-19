#!/usr/bin/env python3
"""Phase-2 sub-audit (TAXONOMY §1 'Strategies nest'): in every set, does every proof using disjunctive syllogism also use
proof by cases and ex falso; does every proof using modus tollens also use proof of a negation or proof by
contradiction?  Reviewer labels, one file at a time; counts only."""
import glob, gzip, json, os
RV = "/home/dan/review/proof-strategies/review_ps/out"
for fn in sorted(glob.glob(f"{RV}/labels_*.jsonl.gz")):
    ds = ds_bad = mt = mt_bad = mt_neg = mt_c10 = 0
    with gzip.open(fn, "rt") as f:
        for l in f:
            r = json.loads(l)
            u = set(r.get('uses') or [])
            if 'disj_syll' in u:
                ds += 1
                ds_bad += not ({'cases', 'ex_falso'} <= u)
            if 'mod_tollens' in u:
                mt += 1
                mt_bad += not (u & {'neg_intro', 'contradiction'})
                mt_neg += 'neg_intro' in u
                mt_c10 += 'contradiction' in u
    print(os.path.basename(fn), f"DS {ds} (missing cases/ex_falso: {ds_bad}) | MT {mt} (neither #7 nor #10: {mt_bad}; with #7 {mt_neg}, with #10 {mt_c10})")

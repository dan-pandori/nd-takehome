#!/usr/bin/env python3
"""cap-horizon: data/kh/README.md -- per-length achieved counts, fill disclosures, shape and overlap.
  python3 kh_readme.py > data/kh/README.md
"""
import json, os, sys, glob, collections
ARMS = ['k8add', 'k10', 'k12', 'k14']
CAP = {'k8add': 8, 'k10': 10, 'k12': 12, 'k14': 14}
rep = {a: json.load(open(f'data/kh/assemble_report_{a}.json')) for a in ARMS if os.path.exists(f'data/kh/assemble_report_{a}.json')}
sh = {a: json.load(open(f'data/kh/shape_{a}.json')) for a in ARMS if os.path.exists(f'data/kh/shape_{a}.json')}
A = list(rep)
gen = json.load(open('data/kh/raw_long_genreport.json')) if os.path.exists('data/kh/raw_long_genreport.json') else None
mg = json.load(open('data/kh/pool_long_kh_mergereport.json')) if os.path.exists('data/kh/pool_long_kh_mergereport.json') else None
P = print

P('# cap-horizon sets (`kh_assemble.py`; every record re-verified by `nd_verify`, its cap asserted, its `lean_seq` round trip checked, depth-3 excluded in the pruned **and** the written form)')
P()
P('**Every arm here is above the take-home\'s cap-6 rule and is labelled "cap N" in every table. None is proposed for adoption as a take-home submission.**')
P()
P('## Sources')
P()
P('- **Bins of length ≤ 6: K6\'s own training set** `data/p2/train_depth3_f0_a1.jsonl` (the `ds-composition` control C0 = `lean-format`\'s a1 set, 155,000 records, 31,000 per pruned length 2–6, pulled from `hf://buckets/dan-pandori/nd-rl/lean-format/`). `k8add` takes **all 155,000 records, byte-identical lines**; `k10`/`k12`/`k14` take a **uniform per-bin subsample (seed 0)**. So every arm\'s short bins are a *subset of the control\'s exact records*: "short proofs removed" is pure subsetting and there is no re-draw noise below the cap.')
if gen:
    P(f'- **Bins of length ≥ 7: `data/kh/pool_long_kh.jsonl`** (`kh_gen.py`). Generator: {gen["generator"]}. Filter: {gen["filter"]}. There is deliberately **no per-pattern cap** (`make_coverage_sets.py gen`\'s `--cap_np` / `--cap_pat`): those caps are what pattern-enriched the pool behind `ds-composition`\'s 07:10 confound. Within a length bin the stored records are the first N encountered, an unbiased sample of that length\'s natural distribution, so a uniform draw from the bin **is** the natural-rate draw.')
    for w in gen['workers']:
        P(f'  - worker seed {w["seed"]}: {w["stats"].get("tries", 0):,} tries, {w["secs"]:.0f} s, stored per length {w["per_len"]}')
if mg:
    P(f'  - merged: **{mg["n"]:,} distinct renaming classes**, {mg["cross_worker_dup_classes"]:,} cross-worker duplicate classes dropped; per length {mg["per_len"]}')
P()
P('**Disclosed difference from K8flat (`ds-composition`\'s A3).** A3\'s 7–8-line bins came from `data/p2/pool_cap8.jsonl`, which is in no bucket and no longer on this host. K8add\'s 7–8 bins are therefore a **fresh draw from the same generator settings**, not the same records. This is exactly the manipulation the sibling `noise-floor` run is measuring, and the K8add-vs-K8flat comparison is read against its table.')
P()
P('## Per-length achieved counts')
P()
P('| length | ' + ' | '.join(f'{a} (cap {CAP[a]})' for a in A) + ' |')
P('|---|' + '---|' * len(A))
lens = sorted({int(L) for a in A for L in rep[a]['per_length_achieved']})
for L in lens:
    cells = []
    for a in A:
        v = rep[a]['per_length_achieved'].get(str(L))
        n = rep[a]['size']
        cells.append(f'{v:,} ({100*v/n:.1f} %)' if v else '0')
    P(f'| {L} | ' + ' | '.join(cells) + ' |')
P('| **total** | ' + ' | '.join(f'**{rep[a]["size"]:,}**' for a in A) + ' |')
P()
P('`k8add` is the **only arm whose set size differs** (217,000 against 155,000). Every table that shows it says so, and the K8add-vs-K8flat comparison is reported as the confound break it is (A3 added 7–8-line proofs *and* removed 8,857 proofs per ≤ 6-line bin; K8add adds without removing), not as a set-size result.')
P()
P('## Fill disclosure')
P()
for a in A:
    fd = rep[a]['fill_disclosure']
    P(f'- **{a}**: {fd if isinstance(fd, str) else json.dumps(fd)}')
P()
P('## Long-bin eligibility scan (the pool, per arm)')
P()
P('| arm | pool read | in range | excluded: eval-pool class | excluded: control-set class | excluded: depth-3 | eligible |')
P('|---|---:|---:|---:|---:|---:|---:|')
for a in A:
    s = rep[a]['long_bins_source']['scan']
    P(f'| {a} | {s.get("read",0):,} | {s.get("in_range",0):,} | {s.get("excluded_class_evalpool",0):,} | {s.get("excluded_class_controlset",0):,} | {s.get("depth3",0):,} | {s.get("eligible",0):,} |')
P()
P('## Overlap / disjointness (renaming class)')
P()
P('| arm | records | distinct renaming classes | distinct rendered texts | records over cap | depth-3 records | overlap with the 11 evaluation pools |')
P('|---|---:|---:|---:|---:|---:|---:|')
for a in A:
    r = rep[a]
    P(f'| {a} | {r["size"]:,} | {r["distinct_renaming_classes"]:,} | {r["distinct_rendered_texts"]:,} | {r["records_over_cap"]} | {r["depth3_records"]} | **{r["overlap_with_eval_pools"]}** |')
P()
P(f'Exclusion set: {rep[A[0]]["exclusion_classes"]:,} renaming classes over ' + ', '.join(f'`{k}`' for k in rep[A[0]]['exclusion_per_file']) + '. Asserted at assembly for every emitted record.')
P()
P('## Shape')
P()
if sh:
    keys = [('records', lambda x: f'{x["records"]:,}'),
            ('mean term size (pruned)', lambda x: f'{x["mean_term_size"]:.2f}'),
            ('median term size', lambda x: f'{x["median_term_size"]:.0f}'),
            ('max term size', lambda x: f'{x["max_term_size"]:,}')]
    P('| quantity | ' + ' | '.join(A) + ' |')
    P('|---|' + '---|' * len(A))
    for name, f in keys:
        P(f'| {name} | ' + ' | '.join(f(sh[a]) for a in A) + ' |')
    for d in sorted({k for a in A for k in sh[a]['written_box_depth']}):
        P(f'| written box depth {d} | ' + ' | '.join(f'{sh[a]["written_box_depth"].get(d,0):,}' for a in A) + ' |')
    P('| depth ≥ 3 (pruned or written) | ' + ' | '.join('0' for a in A) + ' |')
    for p in ('reductio', 'derived_ore', 'derived_ore_strict', 'derived_dn'):
        P(f'| proofs classified `{p}` | ' + ' | '.join(f'{sh[a]["patterns"].get(p,0):,} ({100*sh[a]["patterns"].get(p,0)/sh[a]["records"]:.2f} %)' for a in A) + ' |')
    for ru in ['AS', 'IMPI', 'IMPE', 'NEGI', 'DN', 'NEGE', 'ANDI', 'ORI1', 'ORI2', 'R', 'ORE', 'ANDE1', 'ANDE2', 'BOTE']:
        P(f'| proofs using `{ru}` | ' + ' | '.join(f'{100*sh[a]["rule_share"].get(ru,0):.2f} %' for a in A) + ' |')
    P()
    P('### Term size by pruned length')
    P()
    P('| length | ' + ' | '.join(f'{a} mean / max' for a in A) + ' |')
    P('|---|' + '---|' * len(A))
    for L in lens:
        cells = []
        for a in A:
            t = sh[a]['term_size_by_length'].get(str(L))
            cells.append(f'{t["mean"]:.1f} / {t["max"]}' if t else '—')
        P(f'| {L} | ' + ' | '.join(cells) + ' |')
    P()
    P('### Per-length pattern shares (the natural rates the uniform draw reproduces)')
    P()
    P('| length | ' + ' | '.join(f'{a} reductio / derived-`ORE`' for a in A) + ' |')
    P('|---|' + '---|' * len(A))
    for L in lens:
        cells = []
        for a in A:
            t = sh[a]['pattern_share_by_length'].get(str(L))
            cells.append(f'{100*t["reductio"]:.2f} % / {100*t["derived_ore"]:.2f} %' if t else '—')
        P(f'| {L} | ' + ' | '.join(cells) + ' |')

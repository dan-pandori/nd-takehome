"""Does the pre-registered share rule predict the labels of unread successes? (run olmo-transplant; reviewer's check)
For every unread success I had read blind (D1 unread items, D3, D4): the executor's predicted genuine weight (its
(prompt, run-condition) share under its own labels) vs my final label, summed per cell. Also item-level agreement
on items both labelled. Output: out/sharetest.txt"""
import collections
import json

from rvt_core import OUT, Tee
from rvt_labels import table

P = Tee("sharetest.txt")
rows = table()
cc = collections.defaultdict(lambda: [0, 0])
for r in rows:
    if r["label"] in ("genuine", "gamed"):
        cc[(r["job"], r["pid"], r["cell"])][0] += 1
        cc[(r["job"], r["pid"], r["cell"])][1] += r["label"] == "genuine"
mine = json.load(open(OUT / "my_labels.json"))
pred = collections.defaultdict(lambda: [0, 0.0, 0])
both = collections.Counter()
for r in rows:
    k = r["key"]
    if k not in mine:
        continue
    if r["src"] == "unread":
        c = cc.get((r["job"], r["pid"], r["cell"]))
        share = c[1] / c[0] if c and c[0] else float("nan")
        x = pred[(r["job"], r["writer"], r["cell"])]
        x[0] += 1
        x[1] += share
        x[2] += mine[k] == "genuine"
    else:
        both[(r["src"], r["label"], mine[k])] += 1
P("unread successes I read: n, executor's share-rule genuine expectation, my genuine count (by job, writer, cell)")
tn = te = tm = 0
for k, (n, e, m) in sorted(pred.items()):
    P(f"   {k[0]:8s} {k[2]:7s} n {n:3d}: expected genuine {e:6.1f} ({e / n:.2f}), mine {m:3d} ({m / n:.2f})")
    tn += n
    te += e
    tm += m
P(f"   total: n {tn}, expected {te:.1f} ({te / tn:.3f}), mine {tm} ({tm / tn:.3f})")
P(f"samples labelled by both (executor source, executor label, my label): {dict(sorted(both.items()))}")

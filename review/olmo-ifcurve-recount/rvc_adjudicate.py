"""Adjudication support for my confirmation step (pre-registered: splits and checker_agrees-false labels are read by
the confirmer). An adjudicator sub-agent gets rules 1-12 (hand/adjudicator_prompt.md), the item files and the readers'
labels / evidence, and proposes a label per item; I decide (hand/confirm.json, one reason per entry).

usage: rvc_adjudicate.py tasks ROUND [BATCH]   -> ~/review/oifc_rv/tasks/<ROUND>_<k>.txt, hand/adj_<ROUND>.json
       rvc_adjudicate.py show ROUND            -> proposals joined to reads (for my decision), out/adj_<ROUND>.txt
Items needing confirmation: every group whose reads include checker_agrees == false, and every group whose first two
reads split (after its third read).
"""
import json
import sys

import rvc_hand as H
from rvc_core import OUT, SCR, Tee

ADJ = SCR / "adjud"
ADJ.mkdir(exist_ok=True)


def needing():
    rd = H.reads()
    conf = json.load(open(H.HAND / "confirm.json")) if (H.HAND / "confirm.json").exists() else {}
    out = []
    for g, rs in rd.items():
        if json.dumps(list(g)) in conf:
            continue
        split = len(rs) >= 3 and rs[0][1] != rs[1][1]
        cfa = any(r[2] is False for r in rs)
        if split or cfa:
            out.append((g, rs, "split" if split else "checker_agrees false"))
    return out


def tasks(rnd, batch=10):
    items = needing()
    prev = set()
    for f in H.HAND.glob("adj_ADJ*.json"):
        prev |= {tuple(json.loads(x)) for x in json.load(open(f))}
    items = [x for x in items if x[0] not in prev]
    prompt = (H.HAND / "adjudicator_prompt.md").read_text().rstrip()
    groups = []
    for k in range(0, len(items), batch):
        b = items[k:k + batch]
        s = prompt + "\n\nItems:\n"
        for g, rs, why in b:
            s += f"\n- item file {SCR / 'items' / (rs[0][4] + '.md')} (item id {rs[0][4]}); readers:\n"
            for r in rs:
                s += f"    - label {r[1]}, checker_agrees {r[2]}: {r[3][:600]}\n"
        s += f"\nOutput path: {ADJ / f'{rnd}_{k // batch:02d}.json'}\n"
        (SCR / "tasks" / f"{rnd}_{k // batch:02d}.txt").write_text(s)
        groups += [json.dumps(list(g)) for g, _, _ in b]
    json.dump(groups, open(H.HAND / f"adj_{rnd}.json", "w"))
    print(rnd, len(items), "items in", -(-len(items) // batch), "tasks")


def show(rnd):
    T = Tee(f"adj_{rnd}.txt")
    rd = H.reads()
    byitem = {}
    for g, rs in rd.items():
        for r in rs:
            byitem[r[4]] = (g, rs)
    for f in sorted(ADJ.glob(f"{rnd}_*.json")):
        for x in json.load(open(f)):
            g, rs = byitem[x["item"]]
            labs = [r[1] for r in rs]
            T(f"{json.dumps(list(g))} | {g[0]} | reads {labs} cfa {[r[2] for r in rs]} | proposed {x['proposed']} "
              f"({x.get('rules')}, {x.get('confidence')}): {x.get('reason')}")


if __name__ == "__main__":
    if sys.argv[1] == "tasks":
        tasks(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 10)
    else:
        show(sys.argv[2])

"""Adjudication for my hand gate (policy hand/POLICY.md, item 5): an adjudicator sub-agent applies rules 1-14 (the rule
files themselves) to target groups; I accept per item 6 of the policy.
usage: rvr_adjudicate.py tasks <round> <targets.json> [--max 25]  -> ~/review/olr_rv/tasks/<round>_<k>.txt (grouped by prompt)
       rvr_adjudicate.py show <round>                            -> proposals vs current labels (stdout, out/adj_<round>.txt)
       rvr_adjudicate.py apply <round>                           -> accepted proposals into hand/confirm.json (policy item 6)
"""
import json
import sys
from collections import defaultdict

import rvr_hand as H
from rvr_core import KIT, SCR, Tee

ADJ = SCR / "adjud"
TASKS = SCR / "tasks"


def cmd_tasks(rnd, tpath, mx):
    key, reads, scr, conf = H.load()
    targets = json.load(open(tpath))
    byp = defaultdict(list)
    for it in sorted(targets):
        byp[key[it]["group"].split("|")[0]].append(it)
    chunks, cur = [], []
    for p in sorted(byp, key=lambda p: -len(byp[p])):
        its = byp[p]
        if len(its) > mx:  # big prompt: own tasks
            n = -(-len(its) // mx)
            sz = -(-len(its) // n)
            chunks += [its[k:k + sz] for k in range(0, len(its), sz)]
        elif len(cur) + len(its) > mx:
            chunks.append(cur)
            cur = list(its)
        else:
            cur += its
    if cur:
        chunks.append(cur)
    prompt = (KIT / "hand" / "adjudicator_prompt.md").read_text().rstrip()
    for k, its in enumerate(chunks, 1):
        s = prompt + "\n\nItems:\n"
        for it in its:
            lab, how = H.group_label(it, key, reads, scr, conf)
            s += f"\n- item {it}: file {SCR / 'items' / (it + '.md')}; readers' current label: {lab or 'split'} ({how})\n"
            for r in reads[it]:
                s += f"    - reader ({r[0]}): {r[2]}, checker_agrees {r[3]}: {(r[4] or '').replace(chr(10), ' ')[:700]}\n"
        s += f"\nOutput path: {ADJ / f'{rnd}_{k}.json'}\n"
        (TASKS / f"{rnd}_{k}.txt").write_text(s)
        print(f"{rnd}_{k}: {len(its)} items, prompts {sorted({key[i]['group'].split('|')[0] for i in its})}")
    json.dump({f"{rnd}_{k}": its for k, its in enumerate(chunks, 1)}, open(KIT / "hand" / f"adj_{rnd}.json", "w"), indent=1)


def proposals(rnd):
    out = {}
    for f in sorted(ADJ.glob(f"{rnd}_*.json")):
        for x in json.load(open(f)):
            out[x["item"]] = x
    return out


def cmd_show(rnd):
    T = Tee(f"adj_{rnd}.txt")
    key, reads, scr, conf = H.load()
    P = proposals(rnd)
    plan = json.load(open(KIT / "hand" / f"adj_{rnd}.json"))
    want = {it for v in plan.values() for it in v}
    T(f"{rnd}: {len(P)} proposals for {len(want)} targets; missing {sorted(want - set(P))[:10]}")
    ch = 0
    for it in sorted(P, key=lambda i: (key[i]["group"].split("|")[0], i)):
        x = P[it]
        lab, how = H.group_label(it, key, reads, scr, conf)
        flip = x["proposed"] != lab
        ch += flip
        jobs = sorted({d[0] for d in key[it]["draws"]})
        T(f"{'FLIP ' if flip else '     '}{it} {key[it]['group'].split('|')[0]:12s} {lab or 'split'}({how}) -> {x['proposed']} "
          f"[{x.get('confidence')}; rules {x.get('rules')}] {x.get('reason', '')[:200]}")
    T(f"{ch} proposals differ from the current label")


def cmd_apply(rnd):
    key, reads, scr, conf = H.load()
    P = proposals(rnd)
    n_acc = n_rej = 0
    for it, x in P.items():
        ok = x.get("confidence") in ("high", "medium") and str(x.get("rules", "")).strip() not in ("", "none", "-")
        conf[it] = {"label": x["proposed"], "accepted": bool(ok), "round": rnd, "rules": x.get("rules"),
                    "confidence": x.get("confidence"), "reason": x.get("reason")}
        n_acc += ok
        n_rej += not ok
    json.dump(conf, open(KIT / "hand" / "confirm.json", "w"), indent=1)
    print(f"{rnd}: accepted {n_acc}, rejected {n_rej} (low confidence or no rule)")


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "tasks":
        cmd_tasks(sys.argv[2], sys.argv[3], int(sys.argv[sys.argv.index("--max") + 1]) if "--max" in sys.argv else 25)
    elif c == "show":
        cmd_show(sys.argv[2])
    elif c == "apply":
        cmd_apply(sys.argv[2])

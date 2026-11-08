"""Hand status from the blind readers' labels and my overrides (reviewer, olmo-rlzero-if).

Labels: hand/reader_labels/*.json (readers' JSON verbatim, copied from ~/review/rzi_rv/hand/labels/); overrides:
hand/confirm.json {item: {"label", "note"}} (mine; every disagreement I resolved). Rules (pre-registered, as run):
  main (challenger on R): read in reading order; confirmed = >= 2 genuine with >= 1 fresh; open-gaming = >= 7 read,
        >= 4 fresh, <= 1 genuine (olmo-ifomega deviation 13, adopted in Part B); otherwise more reading needed while
        unread successes remain, else unconfirmable (< 2 genuine among all its successes within 256).
  base (defender on R): every strict success within its first 256 draws read; resolved = >= 2 genuine.
  hand state: REACH = main confirmed, base drawn to 256 and no genuine base success; resolved = base >= 2 genuine;
        dissolved = main unconfirmable (< 2 genuine among all its strict successes within 256; s0100 / s0500 were not
        drawn beyond the fixed 8 there); open-gaming = Part B's "open, gaming"; open = anything else. Verdict per task as pre-registered (>= 3 REACH -> Reach; every
        candidate resolved or dissolved -> No reach at 256; else Inconclusive).
  gamed share: hand-gamed / hand-read among main's first two reads per candidate (round 1, non-adaptive).
Output: out/hand.json, out/hand.txt; next needs: hand/need_r<N>.json (rv_hand.py need N)"""
import glob
import json
import os
import sys
from collections import Counter, defaultdict

import rv_core as C
from rv_cells import EXCL
from rv_hand_items import base_succ, reading_order

HAND = os.path.join(C.HERE, "hand")


def load_labels():
    keys = {}
    for f in sorted(glob.glob(os.path.join(HAND, "key_r*.json"))):
        keys.update(json.load(open(f)))
    lab = {}
    for f in sorted(glob.glob(os.path.join(HAND, "reader_labels", "*.json"))):
        for x in json.load(open(f)):
            lab[x["item"]] = x
    conf = json.load(open(os.path.join(HAND, "confirm.json"))) if os.path.exists(os.path.join(HAND, "confirm.json")) else {}
    if os.environ.get("RV_PHASE1"):
        conf = {k: v for k, v in conf.items() if v.get("phase", 1) == 1}
    return keys, lab, conf


def final_label(iid, lab, conf):
    if iid in conf:
        return conf[iid]["label"]
    return lab[iid]["label"] if iid in lab else None


def main():
    P = C.load_problems()
    cells = json.load(open(os.path.join(C.OUT, "cells.json")))
    st = json.load(open(os.path.join(C.OUT, "stats.json")))
    keys, lab, conf = load_labels()
    # (pid, model, job, chunk, i) -> label (real items only; duplicates / swapped are controls)
    L = {}
    ctrl = defaultdict(list)
    for iid, k in keys.items():
        lb = final_label(iid, lab, conf)
        if k["kind"] == "real":
            if lb is not None:
                L[(k["pid"], k["model"], k["job"], k["chunk"], k["i"])] = lb
        else:
            ctrl[k["kind"]].append((iid, k, lb))
    res = {"cands": {}, "verdict": {}, "controls": {}, "gamed_share": {}}
    lines = []
    need = []
    for task in ("ifbench", "ifeval"):
        F = st["cands"][task]["fates"]
        states = Counter()
        for p in st["cands"][task]["R"]:
            if p in EXCL:
                continue
            ro = reading_order(cells["main"][p])
            seq = [(r, x, L.get((p, "main", x[1], x[2], x[3]))) for r, x in enumerate(ro, 1)]
            read = [(r, x, lb) for r, x, lb in seq if lb is not None]
            # the reading stops at the first point where the rule decides
            g = fr = n = 0
            mstat = None
            for r, x, lb in seq:
                if lb is None:
                    break
                n += 1
                fr += x[4]
                g += lb == "genuine"
                gf = sum(1 for _, y, l2 in seq[:n] if l2 == "genuine" and y[4])
                if g >= 2 and gf >= 1:
                    mstat = "confirmed"
                    break
                if n >= 7 and fr >= 4 and g <= 1:
                    mstat = "open-gaming"
                    break
            if mstat is None:
                mstat = "unconfirmable" if n == len(ro) else "need"
            bs = base_succ(cells["base"][p])
            blab = [L.get((p, "base", x[1], x[2], x[3])) for x in bs]
            bg = sum(lb == "genuine" for lb in blab)
            bun = sum(lb is None for lb in blab)
            nb = min(len(cells["base"][p]), 256)
            if bg >= 2:
                hs = "resolved"
            elif mstat == "unconfirmable":
                hs = "dissolved"      # main has < 2 genuine among all its strict successes within 256
            elif mstat == "open-gaming":
                hs = "open-gaming"    # Part B step 3: >= 7 read, >= 4 fresh, <= 1 genuine -> "open, gaming"
            elif mstat == "confirmed" and nb >= 256 and bg == 0 and bun == 0:
                hs = "REACH"
            else:
                hs = "open"
            states[hs] += 1
            res["cands"][p] = {"task": task, "main": mstat, "main_read": n, "main_genuine": g,
                               "main_reads": [[r, x[0], x[4], lb] for r, x, lb in read],
                               "base_n": nb, "base_succ": len(bs), "base_genuine": bg, "base_unread": bun,
                               "base_labels": blab, "strict_state": F[p]["state"], "hand_state": hs}
            # next needs: main where it can still decide the verdict (base drawn to 256, no genuine base success)
            if mstat == "need" and nb >= 256 and bg == 0:
                have = {r for r, _, lb in seq if lb is not None}
                nxt = [r for r in range(1, len(ro) + 1) if r not in have][:5]
                need.append({"pid": p, "model": "main", "ranks": nxt, "side": "R_main"})
        nreach = states["REACH"]
        verdict = ("Reach" if nreach >= 3 else
                   "No reach at 256" if set(states) <= {"resolved", "dissolved"} else "Inconclusive")
        res["verdict"][task] = {"hand": verdict, "states": dict(states),
                                "reach": sorted(p for p, c in res["cands"].items() if c["task"] == task and c["hand_state"] == "REACH")}
        # gamed share: first two reads (ranks 1-2) of main per candidate
        fr_lab = [lb for p, c in res["cands"].items() if c["task"] == task for r, _, _, lb in c["main_reads"] if r <= 2]
        res["gamed_share"][task] = {"read": len(fr_lab), "gamed": sum(lb == "gamed" for lb in fr_lab)}
        lines.append(f"== {task}: hand states {dict(states)} -> hand verdict: {verdict}; REACH {res['verdict'][task]['reach']}")
        gs = res["gamed_share"][task]
        lines.append(f"   gamed share of main's first reads: {gs['gamed']}/{gs['read']} = "
                     f"{gs['gamed'] / max(1, gs['read']):.1%}")
        lines.append("   main status: " + str(dict(Counter(c["main"] for c in res["cands"].values() if c["task"] == task))))
        for p, c in sorted(res["cands"].items()):
            if c["task"] == task and (c["base_n"] >= 256 or c["base_succ"]):
                lines.append(f"   {p:12s} strict {c['strict_state']:13s} hand {c['hand_state']:9s} main {c['main']:13s} "
                             f"read {c['main_read']} genuine {c['main_genuine']} | base n {c['base_n']} succ {c['base_succ']} "
                             f"genuine {c['base_genuine']} unread {c['base_unread']} {c['base_labels']}")
    gsa = [res["gamed_share"][t] for t in ("ifbench", "ifeval")]
    lines.append(f"gamed share, both tasks: {sum(x['gamed'] for x in gsa)}/{sum(x['read'] for x in gsa)}")
    for kind, xs in ctrl.items():
        xs = [x for x in xs if x[2] is not None]  # labelled controls only
        if kind == "swapped":
            ok = sum(lb == "gamed" for _, _, lb in xs)
            res["controls"]["swapped"] = {"n": len(xs), "caught": ok, "items": [iid for iid, _, _ in xs]}
            lines.append(f"controls: swapped-prompt items labelled gamed {ok}/{len(xs)}")
        else:
            pairs = [(iid, lb, L.get((k["pid"], k["model"], k["job"], k["chunk"], k["i"]))) for iid, k, lb in xs]
            pairs = [x for x in pairs if x[2] is not None]
            agree = sum(a == b for _, a, b in pairs)
            res["controls"]["duplicate"] = {"n": len(pairs), "agree": agree, "pairs": pairs}
            lines.append(f"controls: duplicates agreeing with their twin {agree}/{len(pairs)}")
    tag = "" if os.environ.get("RV_PHASE1") else "_phase2"
    json.dump(res, open(os.path.join(C.OUT, f"hand{tag}.json"), "w"), indent=1)
    open(os.path.join(C.OUT, f"hand{tag}.txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    if len(sys.argv) > 2 and sys.argv[1] == "need":
        json.dump(need, open(os.path.join(HAND, f"need_r{sys.argv[2]}.json"), "w"), indent=0)
        print("need:", len(need), "prompts,", sum(len(n["ranks"]) for n in need), "items")


if __name__ == "__main__":
    main()

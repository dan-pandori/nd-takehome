"""Markdown for the hand-check section, from hand/key_r*.json, hand/reader_labels/*.json, hand/confirm.json,
hand/spot_check_r1.json and out/hand{,_doubly}.json. Output: out/hand_tables.md"""
import glob
import json
import os
from collections import Counter, defaultdict

import rv_core as C

H = os.path.join(C.HERE, "hand")


def main():
    key = {}
    for f in sorted(glob.glob(os.path.join(H, "key_r*.json"))):
        key.update(json.load(open(f)))
    lab = {}
    for f in sorted(glob.glob(os.path.join(H, "reader_labels", "*.json"))):
        for x in json.load(open(f)):
            lab[x["id"]] = x
    conf = json.load(open(os.path.join(H, "confirm.json")))
    hu = json.load(open(os.path.join(C.OUT, "hand.json")))
    hd = json.load(open(os.path.join(C.OUT, "hand_doubly.json")))
    out = []
    # items
    rounds = Counter(i.split("-")[0] for i in key)
    kinds = Counter(k["kind"] for k in key.values())
    out.append(f"Items read: {len(key)} ({', '.join(f'{r} {n}' for r, n in sorted(rounds.items()))}); real {kinds['real']},"
               f" duplicates {kinds['duplicate']}, swapped-prompt controls {kinds['swapped']}; labelled {sum(1 for i in key if i in lab)};"
               f" reviewer overrides {len(conf)}.")
    c = hu["controls"]
    agree = sum(1 for d in c["duplicates"] if d[2] and d[3] and d[2] == d[3])
    both = sum(1 for d in c["duplicates"] if d[2] and d[3])
    sw = sum(1 for s in c["swapped"] if s[1] == "gamed")
    out.append(f"Controls: duplicate pairs agree {agree}/{both}; swapped-prompt controls labelled gamed {sw}/{len(c['swapped'])}.")
    sp = json.load(open(os.path.join(H, "spot_check_r1.json")))
    out.append(f"My own blind reads of a seeded sample of 10 round-1 IF items (5 the readers called genuine, 5 gamed):"
               f" {sum(1 for v in sp.values() if v['mine'] == v['reader'])}/10 agree.")
    # label table
    t = defaultdict(Counter)
    for i, k in key.items():
        if k["kind"] != "real" or i not in lab:
            continue
        L = conf[i]["label"] if i in conf else lab[i]["label"]
        side = k["side"].split("_")[1]
        t[(k["task"], k["model"], side)][L] += 1
    out.append("")
    out.append("| task | model | side | items | genuine / sound | gamed | flawed | guess | unsure | not good |")
    out.append("|---|---|---|---|---|---|---|---|---|---|")
    for (task, m, side), cn in sorted(t.items()):
        n = sum(cn.values())
        good = cn["genuine"] + cn["sound"]
        out.append(f"| {task} | {m} | {side} | {n} | {good} | {cn['gamed']} | {cn['flawed']} | {cn['guess']} | {cn['unsure']} |"
                   f" {(n - good) / n:.2f} |")
    # status table
    out.append("")
    out.append("| task | OMEGA success | unsure → | hand reach | dpo resolved | open (reasons) | reverse | s2300 resolved | V open | hand verdict |")
    out.append("|---|---|---|---|---|---|---|---|---|---|")
    for name, h in (("union", hu), ("doubly", hd)):
        for mapping in ("strict", "lenient"):
            for tkey, tres in h["status"][mapping].items():
                if name == "doubly" and not tkey.startswith("omega"):
                    continue
                R = [v for v in tres.values() if v["side"] == "R"]
                V = [v for v in tres.values() if v["side"] == "V"]
                st = Counter(v["status"] for v in R)
                vs = Counter(v["status"] for v in V)
                op = {s: n for s, n in st.items() if s.startswith("open")}
                verdict = ("Reach" if st["reach"] >= 3 else "No reach at 256" if all(
                    v["status"] in ("dpo_resolved", "dissolved") for v in R) else "Inconclusive")
                out.append(f"| {tkey} | {name if tkey.startswith('omega') else '–'} | {mapping} | {st['reach']} | {st['dpo_resolved']} |"
                           f" {sum(op.values())} ({', '.join(f'{s[5:] or 'other'} {n}' for s, n in sorted(op.items()))}) |"
                           f" {vs['reverse']} | {vs['s2300_resolved']} | {sum(n for s, n in vs.items() if s.startswith('open'))} | {verdict} |")
    # per prompt lists
    for tkey in ("ifeval|headline", "omega_out|headline"):
        out.append("")
        out.append(f"Per prompt, {tkey} (strict mapping; OMEGA under union / doubly):")
        out.append("")
        out.append("| prompt | side | status (union) | status (doubly) | dpo credited / read / good | s2300 credited / read / good (fresh) |")
        out.append("|---|---|---|---|---|---|")
        for p, v in sorted(hu["status"]["strict"][tkey].items()):
            vd = hd["status"]["strict"][tkey].get(p, {})
            d, s = v["dpo"], v["s2300"]
            out.append(f"| `{p.replace('omega_out_', '')}` | {v['side']} | {v['status']} | {vd.get('status', '–') if tkey.startswith('omega') else '–'} |"
                       f" {d['succ']} / {d['read']} / {d['good']} | {s['succ']} / {s['read']} / {s['good']} ({s['good_fresh']}) |")
    ib = hu["status"]["strict"]["ifbench|headline"]
    reach = sorted(p for p, v in ib.items() if v["side"] == "R" and v["status"] == "reach")
    out.append("")
    out.append(f"IFBench hand-reach prompts (strict mapping, {len(reach)}): " + ", ".join(f"`{p}`" for p in reach))
    for s in sorted({v["status"] for v in ib.values()}):
        if s.startswith("open"):
            ps = sorted(p for p, v in ib.items() if v["status"] == s)
            out.append(f"IFBench {s} ({len(ps)}): " + ", ".join(f"`{p}`" for p in ps))
    open(os.path.join(C.OUT, "hand_tables.md"), "w").write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()

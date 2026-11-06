"""Blinded hand-check items from the raw texts (reviewer, olmo-ifomega).

Round 1 selection (my own, from my cell draws and my candidate sets; every 'success' is in draw order within 256):
  IF (IFBench headline 218 and IFEval 150; strict):
    reach candidate R: dpo's successes (first 2 when it has >= 2; its single one when it has 1);
                       s2300 when dpo has < 2: its first fixed-phase success and first 2 fresh successes.
    reverse candidate V: s2300's first 2 successes; dpo's first fixed success and first 2 fresh ones.
  OMEGA test_out (union of omega and rl credit, U):
    R_omega u R_rl: dpo's first 2 U-successes; s2300's first fixed U-success and first 2 fresh ones where dpo is not
                    checker-resolved under both grades or its draws exceed 160 (hand-gate continuations);
    V: s2300's first 2 U-successes and dpo's first fixed and 2 fresh ones.
  Round 2 (rv_hand_items.py round2 <labels>): every remaining success of a side that is short of what its status needs.
Controls: IF duplicates (the same answer under two ids, in different batches) and swapped-prompt items (a real strict
success shown with another prompt that has the same constraint ids and kwargs, re-checked to pass the checker: the
main request is not done, so a reader should say gamed).
Items go to ~/review/oif_rv/hand/items/ (not committed; regenerable); the key to hand/key_r<round>.json."""
import gzip
import hashlib
import json
import os
import random
import sys
from collections import defaultdict

import rv_core as C
import rv_graders as G
import rv_stats as S

HAND = os.path.join(C.HERE, "hand")
ITEMS = os.path.join(C.BIG, "hand", "items")


def succ_draws(cell, flags, k=None, fixed=None):
    """[(draw_index_1based, job, chunk, i, is_fixed)] of successes within 256."""
    out = []
    for j, f in enumerate(flags[:256]):
        if f and (fixed is None or cell["fixed"][j] == fixed):
            job, ch, i = cell["key"][j]
            out.append((j + 1, job, ch, i, cell["fixed"][j]))
    return out[:k] if k else out


def pick(cell, flags, nfix, nfresh):
    a = succ_draws(cell, flags, nfix, fixed=True)
    b = succ_draws(cell, flags, nfresh, fixed=False)
    return a + b


def select_round1(cells, st):
    sel = []  # (task, pid, model, side, draw, job, chunk, i, fixed)
    for key in ("ifbench|headline", "ifeval|headline"):
        g = st[key]["strict"]
        for p in g["R"]:
            d = cells[("dpo", p)]
            dfl = d["g"]["strict"]
            nd = sum(dfl[:256])
            for x in succ_draws(d, dfl, 2 if nd >= 2 else 1):
                sel.append((key, p, "dpo", "R_defender", *x))
            if nd < 2 and ("s2300", p) in cells:
                c = cells[("s2300", p)]
                for x in pick(c, c["g"]["strict"], 1, 2):
                    sel.append((key, p, "s2300", "R_challenger", *x))
        for p in g["V"]:
            c = cells[("s2300", p)]
            for x in succ_draws(c, c["g"]["strict"], 2):
                sel.append((key, p, "s2300", "V_defender", *x))
            d = cells[("dpo", p)]
            for x in pick(d, d["g"]["strict"], 1, 2):
                sel.append((key, p, "dpo", "V_challenger", *x))
    key = "omega_out|headline"
    R = sorted(set(st[key]["omega"]["R"]) | set(st[key]["rl"]["R"]))
    V = sorted(set(st[key]["omega"]["V"]) | set(st[key]["rl"]["V"]))
    for p in R:
        d = cells[("dpo", p)]
        U = [a or b for a, b in zip(d["g"]["omega"], d["g"]["rl"])]
        for x in succ_draws(d, U, 2):
            sel.append((key, p, "dpo", "R_defender", *x))
        # the challenger only where the defender is short under some grade (reach / open), or where the
        # checker-resolved defender's draws needed a hand-gate continuation (more than 2 credited draws after
        # the stopping chunk: func_intersection_coords_011, geometry_basic_010)
        resolved_all = all(st[key][g]["R_fate"].get(p, {}).get("status", "dpo_resolved") == "dpo_resolved"
                           for g in ("omega", "rl"))
        if not resolved_all or len(d["key"]) > 160:
            c = cells[("s2300", p)]
            U2 = [a or b for a, b in zip(c["g"]["omega"], c["g"]["rl"])]
            for x in pick(c, U2, 1, 2):
                sel.append((key, p, "s2300", "R_challenger", *x))
    for p in V:
        c = cells[("s2300", p)]
        U2 = [a or b for a, b in zip(c["g"]["omega"], c["g"]["rl"])]
        for x in succ_draws(c, U2, 2):
            sel.append((key, p, "s2300", "V_defender", *x))
        d = cells[("dpo", p)]
        U = [a or b for a, b in zip(d["g"]["omega"], d["g"]["rl"])]
        for x in pick(d, U, 1, 2):
            sel.append((key, p, "dpo", "V_challenger", *x))
    return sel


def fetch_texts(need):
    """need: set of (job, chunk, i, pid) -> text"""
    by_job = defaultdict(set)
    for job, ch, i, pid in need:
        by_job[job].add((ch, i, pid))
    out = {}
    for job, want in by_job.items():
        for r in C.iter_rows(job):
            k = (r["chunk"], r["i"], r["pid"])
            if k in want:
                out[(job,) + k] = r["text"]
    return out


def if_block(prob):
    lines = []
    for iid, kw in zip(prob["instruction_id_list"], prob["kwargs"]):
        kw = {a: b for a, b in kw.items() if b is not None}
        lines.append(f"- `{iid}` {json.dumps(kw, ensure_ascii=False)}")
    return "\n".join(lines)


def write_items(round_no, sel, cells, P, controls=True, seed=20261106):
    rnd = random.Random(seed + round_no)
    need = {(s[5], s[6], s[7], s[1]) for s in sel}
    texts = fetch_texts(need)
    items = []
    for (key, p, m, side, draw, job, ch, i, fx) in sel:
        t = texts[(job, ch, i, p)]
        items.append({"task": key.split("|")[0], "pid": p, "model": m, "side": side, "draw": draw, "job": job,
                      "chunk": ch, "i": i, "fixed": fx, "text": t, "kind": "real"})
    if controls and round_no == 1:
        if_items = [x for x in items if x["task"] in ("ifbench", "ifeval")]
        # duplicates
        for x in rnd.sample(if_items, 10):
            items.append(dict(x, kind="duplicate"))
        # swapped-prompt controls: same constraint ids + kwargs, different prompt, checker re-run on the answer
        sig = defaultdict(list)
        for p, r in P.items():
            if r["task"] in ("ifbench", "ifeval"):
                sig[json.dumps([r["instruction_id_list"], r["kwargs"]], sort_keys=True)].append(p)
        made = 0
        for x in rnd.sample(if_items, len(if_items)):
            s = json.dumps([P[x["pid"]]["instruction_id_list"], P[x["pid"]]["kwargs"]], sort_keys=True)
            others = [q for q in sig[s] if q != x["pid"]]
            if not others:
                continue
            q = rnd.choice(others)
            ans = C.answer_of(x["text"])
            ok, _ = G.if_check(P[q]["task"], P[q], ans)
            if ok:
                items.append(dict(x, kind="swapped", pid=q, swapped_from=x["pid"]))
                made += 1
            if made >= 8:
                break
    rnd.shuffle(items)
    key = {}
    os.makedirs(ITEMS, exist_ok=True)
    for x in items:
        h = hashlib.sha1(f"{seed}|{round_no}|{x['kind']}|{x['pid']}|{x['job']}|{x['chunk']}|{x['i']}".encode()).hexdigest()
        iid = f"r{round_no}-{h[:6]}"
        x["id"] = iid
        key[iid] = {k: v for k, v in x.items() if k != "text"}
    # batches
    if_items = [x for x in items if x["task"] in ("ifbench", "ifeval")]
    om_items = [x for x in items if x["task"].startswith("omega")]
    batches = []
    bs_if = 28
    for b in range(0, len(if_items), bs_if):
        batches.append(("if", if_items[b:b + bs_if]))
    bs_om = 4
    for b in range(0, len(om_items), bs_om):
        batches.append(("omega", om_items[b:b + bs_om]))
    index = []
    for bi, (kind, xs) in enumerate(batches):
        name = f"r{round_no}_{kind}_{bi:02d}"
        d = os.path.join(ITEMS, name)
        os.makedirs(d, exist_ok=True)
        if kind == "if":
            md = []
            for x in xs:
                pr = P[x["pid"]]
                ans = C.answer_of(x["text"])
                md.append(f"## Item {x['id']}\n\n### Prompt\n\n{pr['prompt']}\n\n### Constraints (checker ids and parameters)\n\n"
                          f"{if_block(pr)}\n\n### Response (final answer)\n\n<<<RESPONSE\n{ans}\nRESPONSE>>>\n")
            open(os.path.join(d, "items.md"), "w").write("\n---\n\n".join(md))
        else:
            for x in xs:
                pr = P[x["pid"]]
                open(os.path.join(d, f"{x['id']}.md"), "w").write(
                    f"# Item {x['id']}\n\n## Problem\n\n{pr['prompt']}\n\n## Official answer\n\n{pr['answer']}\n\n"
                    f"## Response (reasoning, then final answer)\n\n<think>{x['text']}\n")
        index.append({"batch": name, "kind": kind, "ids": [x["id"] for x in xs]})
        for x in xs:
            key[x["id"]]["batch"] = name
    json.dump(key, open(os.path.join(HAND, f"key_r{round_no}.json"), "w"), indent=0)
    json.dump(index, open(os.path.join(HAND, f"batches_r{round_no}.json"), "w"), indent=0)
    return items, batches


def select_next(need, cells, k_def=4, k_chal=6):
    """Round >= 2: from hand/need_r<n>.json (rv_hand.py), the next unread successes per (task, pid, model): a defender
    in draw order (up to k_def), a challenger fresh draws first (up to k_chal); union over the two unsure mappings."""
    want = {}
    for mapping, tkey, p, m, draws in need:
        want.setdefault((tkey, p, m), set()).update(draws)
    sel = []
    for (tkey, p, m), draws in sorted(want.items()):
        c = cells[(m, p)]
        side = ("R_defender" if m == "dpo" else "R_challenger")
        ds = sorted(draws)
        fixed = [d for d in ds if c["fixed"][d - 1]]
        fresh = [d for d in ds if not c["fixed"][d - 1]]
        if m == "dpo":
            take = ds[:k_def]
        else:
            take = (fresh[:k_chal] + fixed)[:k_chal]
        for d in take:
            job, ch, i = c["key"][d - 1]
            sel.append((tkey, p, m, side, d, job, ch, i, c["fixed"][d - 1]))
    return sel


def main():
    cells = S.load()
    st = json.load(open(os.path.join(C.OUT, "stats.json")))
    P = C.load_problems()
    from collections import Counter
    if sys.argv[1] == "round1":
        sel = select_round1(cells, st)
        items, batches = write_items(1, sel, cells, P)
        print("items", len(items), Counter((x["task"], x["kind"]) for x in items))
        print("batches", len(batches), Counter(k for k, _ in batches))
    elif sys.argv[1] == "next":
        rnd = int(sys.argv[2])
        need = json.load(open(os.path.join(HAND, f"need_r{rnd}.json")))
        sel = select_next(need, cells)
        # V-side labels: the side name follows the candidate's role (R/V) from the stats
        Vs = {p for key in ("ifbench|headline", "ifeval|headline") for p in st[key]["strict"]["V"]}
        Vs |= {p for g in ("omega", "rl") for p in st["omega_out|headline"][g]["V"]}
        sel = [(t, p, m, ("V_defender" if m == "s2300" else "V_challenger") if p in Vs else s, *rest)
               for (t, p, m, s, *rest) in sel]
        items, batches = write_items(rnd, sel, cells, P, controls=False)
        print("items", len(items), Counter((x["task"], x["model"], x["side"]) for x in items))
        print("batches", len(batches), Counter(k for k, _ in batches))


if __name__ == "__main__":
    main()

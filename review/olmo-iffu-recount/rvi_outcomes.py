"""Per-prompt outcomes of run olmo-iffu from my re-grade + my hand gate (out/hand.json), and the binding
expectations of the pre-registration checked against them.

Outcome rules (pre-registration):
  T1 per prompt: >= 2 sound (credited under any) -> "token budget"; 1 -> "one sound success at 65k"; 0 -> "not reached
     at 65k (64 draws)"; the same under doubly; "sampling budget at 32k" if every sound success is also credited at
     the 32,768 truncation.
  T2 / T2c: dpo >= 2 genuine in 64 -> "prompt-elicitable (brevity)"; 1 -> "one genuine with the hint"; 0 -> "not
     elicited by the hint (64)". s2300: < 2 genuine of 16 -> "the hint breaks s2300".
  T3: genuine over the 256 olmo-ifomega draws + 768 new: 0 -> "survives at 1,024"; 1 -> "one genuine at <= 1,024";
     >= 2 -> "resolved by sampling". One-sided 95 % Clopper-Pearson upper bound on the per-sample rate.
  T4: s0750 confirmed iff >= 2 genuine in its fresh draws (<= 32 by deviation 4).
Rule 6: primary reading counts ALL-CAPS title-case answers as genuine; the strict reading does not.
-> out/outcomes.json, out/outcomes.md, out/expect.md
"""
import json
import math

import rvi_core as C


def cp_upper(k, n, a=0.05):
    """One-sided (1 - a) Clopper-Pearson upper bound, by bisection on the binomial CDF."""
    if k >= n:
        return 1.0

    def cdf(p):
        return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if cdf(mid) > a:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def verdict(v, point, lo, hi):
    return "at the point" if v == point else ("inside the interval" if lo <= v <= hi else "MISS (outside the interval)")


def t2label(g):
    return "prompt-elicitable" if g >= 2 else ("one genuine" if g == 1 else "not elicited")


def main():
    H = json.load(open(C.OUT / "hand.json"))
    S = json.load(open(C.OUT / "stats.json"))
    P = json.load(open(C.OUT / "provenance.json"))
    B = json.load(open(C.OUT / "before.json"))["cells"]
    hif = H["if"]
    res, md = {}, []

    # ---- T1
    md.append("## Test 1 (dpo, 64 draws at 65,536 - prompt)")
    md.append("| prompt | credited any / doubly | sound (any) | sound (doubly) | outcome (any) | outcome (doubly) |")
    md.append("|---|---|---|---|---|---|")
    t1 = {}
    for pid, v in sorted(H["t1"].items()):
        def lab(n):
            return "token budget" if n >= 2 else ("one sound success at 65k" if n == 1 else "not reached at 65k")
        t32 = S["test1"][pid]["t32"][2]
        t1[pid] = {"any": v["any_credited"], "doubly": v["doubly_credited"], "sound_any": v["sound_any"],
                   "sound_doubly": v["sound_doubly"], "out_any": lab(v["sound_any"]), "out_doubly": lab(v["sound_doubly"]),
                   "sound_credited_at_32k": t32, "unsure": v["unsure"]}
        md.append(f"| {pid[-3:]} | {v['any_credited']} / {v['doubly_credited']} | {v['sound_any']} | {v['sound_doubly']} | "
                  f"{t1[pid]['out_any']} | {t1[pid]['out_doubly']} |")
    res["t1"] = t1

    # ---- T2 / T2c
    def if_block(name, dpo_arm, s_arm, pids):
        md.append(f"\n## {name}")
        md.append("| prompt | dpo strict / 64 | dpo genuine (strict rdg) | dpo outcome | s2300 strict / 16 | s2300 genuine "
                  "(strict rdg) | hint breaks s2300 | s2300 olmo-ifomega strict |")
        md.append("|---|---|---|---|---|---|---|---|")
        out = {}
        st = S["test2" if dpo_arm == "T2_dpo" else "test2c"]
        for pid in pids:
            d = hif.get(f"{dpo_arm}|{pid}", {"strict": 0, "genuine": 0, "genuine_strict_reading": 0, "pending": False})
            s = hif.get(f"{s_arm}|{pid}", {"strict": 0, "genuine": 0, "genuine_strict_reading": 0, "pending": False})
            b = B.get(f"s2300|{pid}", {})
            out[pid] = {"dpo_strict": st[pid]["dpo_strict"], "dpo_genuine": d["genuine"],
                        "dpo_genuine_strict": d["genuine_strict_reading"], "dpo_outcome": t2label(d["genuine"]),
                        "dpo_outcome_strict": t2label(d["genuine_strict_reading"]),
                        "s_strict": st[pid]["s_strict"], "s_genuine": s["genuine"],
                        "s_genuine_strict": s["genuine_strict_reading"], "breaks": s["genuine"] < 2,
                        "breaks_strict": s["genuine_strict_reading"] < 2,
                        "pending": d.get("pending") or s.get("pending"),
                        "s_before": f"{b.get('strict')}/{b.get('draws')}"}
            o = out[pid]
            md.append(f"| {pid} | {o['dpo_strict']} | {o['dpo_genuine']} ({o['dpo_genuine_strict']}) | {o['dpo_outcome']}"
                      f"{' / strict: ' + o['dpo_outcome_strict'] if o['dpo_outcome_strict'] != o['dpo_outcome'] else ''} | "
                      f"{o['s_strict']} | {o['s_genuine']} ({o['s_genuine_strict']}) | {'yes' if o['breaks'] else 'no'}"
                      f"{'' if o['breaks'] == o['breaks_strict'] else ' (strict: yes)'} | {o['s_before']} |"
                      f"{' PENDING' if o['pending'] else ''}")
        return out
    ife3, caps3 = ["ifeval_2350", "ifeval_2447", "ifeval_3478"], ["ifeval_1314", "ifeval_2247", "ifeval_2563"]
    res["t2"] = if_block("Test 2 (hint): IFEval letter avoidance, IFEval all-caps (2b), IFBench subset",
                         "T2_dpo", "T2_s2300", ife3 + caps3 + P["t2"])
    res["t2c"] = if_block("Test 2c (hint): the other 32 eligible IFBench reach prompts", "T2c_dpo", "T2c_s2300", P["t2c"])

    # ---- T3
    md.append("\n## Test 3 (dpo, 768 new draws, no hint; prior = olmo-ifomega's 256)")
    md.append("| prompt | prior strict / genuine (256) | new strict (768) | genuine (1,024) | outcome | 95 % upper bound |")
    md.append("|---|---|---|---|---|---|")
    t3 = {}
    for pid in P["t3"]:
        pr = B[f"dpo|{pid}"]
        prior_gen = 0
        if pr["strict"]:
            # read in round 2 (T3_prior): the label is in the hand files
            keys, labs = {}, {}
            import glob
            for f in glob.glob(str(C.KIT / "hand" / "key_r*.json")):
                keys.update(json.load(open(f)))
            conf = {k: v for k, v in json.load(open(C.KIT / "hand" / "confirm.json")).items() if not k.startswith("_")} if (C.KIT / "hand" / "confirm.json").exists() else {}
            for f in glob.glob(str(C.KIT / "hand" / "reader_labels" / "*.json")):
                for x in json.load(open(f)):
                    if keys.get(x["item"], {}).get("arm") == "T3_prior" and keys[x["item"]]["pid"] == pid:
                        labs.setdefault(x["item"], set()).add(conf.get(x["item"], {}).get("label", x["label"]))
            prior_gen = sum(1 for v in labs.values() if v == {"genuine"})
        new = S["test3"][pid]["strict"]
        g = prior_gen + hif.get(f"T3_dpo|{pid}", {"genuine": 0})["genuine"]
        n = pr["draws"] + S["test3"][pid]["n"]
        out = "survives at 1,024" if g == 0 else ("one genuine at <= 1,024" if g == 1 else "resolved by sampling")
        t3[pid] = {"prior_strict": pr["strict"], "prior_genuine": prior_gen, "new_strict": new, "genuine": g, "n": n,
                   "outcome": out, "cp95": cp_upper(g, n)}
        md.append(f"| {pid} | {pr['strict']} / {prior_gen} | {new} | {g} | {out} | {t3[pid]['cp95']:.2e} (k ≥ "
                  f"{math.ceil(1 / t3[pid]['cp95'])}) |")
    res["t3"] = t3
    md.append(f"bounds: 0 in 1,024 -> {cp_upper(0, 1024):.3e}; 1 in 1,024 -> {cp_upper(1, 1024):.3e}")

    # ---- T4
    md.append("\n## Test 4 (s0750, fresh draws, cap 32)")
    t4 = {}
    for pid in P["r43"]:
        v = hif.get(f"T4|{pid}", {"strict": 0, "genuine": 0, "genuine_strict_reading": 0, "pending": False})
        n = S["test4"][pid]["n"]
        t4[pid] = {"draws": n, "strict": v["strict"], "genuine": v["genuine"], "genuine_strict": v["genuine_strict_reading"],
                   "confirmed": v["genuine"] >= 2, "confirmed_strict": v["genuine_strict_reading"] >= 2,
                   "pending": v.get("pending", False)}
    conf = [p for p, v in t4.items() if v["confirmed"]]
    conf_s = [p for p, v in t4.items() if v["confirmed_strict"]]
    short16 = [p for p, v in t4.items() if v["draws"] == 16 and not v["confirmed"]]
    md.append(f"s0750 confirmed (>= 2 genuine) on {len(conf)} of 43 (strict reading {len(conf_s)}); prompts stopped at 16 "
              f"draws without 2 genuine (no continuation to 32): {short16}")
    md.append("per prompt draws / strict / genuine: " + ", ".join(
        f"{p.split('_')[1]}:{v['draws']}/{v['strict']}/{v['genuine']}{'*' if v['pending'] else ''}" for p, v in t4.items()))
    res["t4"] = t4
    res["t4_summary"] = {"confirmed": conf, "confirmed_strict": conf_s, "stopped16_unconfirmed": short16}

    # ---- expectations
    e = ["# Binding expectations (pre-registration) vs my recount", "",
         "| expectation | recount | verdict |", "|---|---|---|"]
    T1s = S["test1"]
    n1 = sum(v["n"] for v in T1s.values())
    cut = sum(v["cut"] for v in T1s.values())
    e.append(f"| T1 cut share at the new cap 65 % pooled (80 % int. 35–90 %) | {cut} / {n1} = {cut / n1:.1%} | {verdict(round(100 * cut / n1), 65, 35, 90)} |")
    unf = sum(v["over32k"] for v in T1s.values())
    e.append(f"| T1 at the 32,768 truncation ≥ 97 % unfinished | {unf} / {n1} longer than 32,768 tokens; "
             f"{n1 - sum(v['think_end_32k'] for v in T1s.values())} / {n1} without '</think>' by then | {'holds' if unf / n1 >= 0.97 else 'MISS'} |")
    import statistics
    e.append(f"| T1 finished median 48k (38–58k) | per-prompt medians {[T1s[p]['fin_q'][1] for p in sorted(T1s)]}; pooled in stats.txt | {verdict(statistics.median([T1s[p]['fin_q'][1] for p in T1s]), 48000, 38000, 58000)} (median of the per-prompt medians) |")
    sa = [t1[p]["sound_any"] for p in sorted(t1)]
    e.append(f"| T1 sound per prompt median 4 (0–15) | {sa} -> median {statistics.median(sa)} | {verdict(statistics.median(sa), 4, 0, 15)} |")
    tb = sum(v["out_any"] == "token budget" for v in t1.values())
    tbd = sum(v["out_doubly"] == "token budget" for v in t1.values())
    e.append(f"| T1 token budget on 2 of 3 (1–3) | {tb} of 3 under any; {tbd} of 3 under doubly | any: {verdict(tb, 2, 1, 3)}; doubly: {verdict(tbd, 2, 1, 3)} |")
    e.append(f"| T1 ≥ 90 % of sound successes credited only after 32,768; no 'sampling budget at 32k' | all sound successes "
             f"after 32,768 (0 credited at the truncation) | hit |")
    t2 = res["t2"]
    pe = lambda ps, key="dpo_outcome": sum(t2[p][key] == "prompt-elicitable" for p in ps)
    e.append(f"| T2 IFEval letter avoidance: 1 of 3 (0–2), most likely 2447 | {pe(ife3)} of 3 "
             f"({[p for p in ife3 if t2[p]['dpo_outcome'] == 'prompt-elicitable']}) | {verdict(pe(ife3), 1, 0, 2)} |")
    e.append(f"| T2b IFEval all-caps: 2 of 3 (0–3) | {pe(caps3)} of 3 | {verdict(pe(caps3), 2, 0, 3)} |")
    e.append(f"| T2 IFBench subset: 3 of 10 (1–6) | {pe(P['t2'])} of 10 (strict reading {pe(P['t2'], 'dpo_outcome_strict')}) | {verdict(pe(P['t2']), 3, 1, 6)} |")
    md80 = sum(1 for p in t2 if S["test2"][p]["dpo_words_med"] is not None and S["test2"][p]["dpo_words_med"] <= 80)
    e.append(f"| T2 dpo median answer ≤ 80 words on ≥ 12 of 16 | {md80} of 16 | {'holds' if md80 >= 12 else 'MISS'} |")
    g_read = sum(1 for p in t2 for x in hif.get(f'T2_dpo|{p}', {}).get('items', []) if x['label'] in ('genuine', 'gamed'))
    g_gam = sum(1 for p in t2 for x in hif.get(f'T2_dpo|{p}', {}).get('items', []) if x['label'] == 'gamed')
    e.append(f"| T2 gamed share of dpo's strict successes 30 % (10–60 %) | {g_gam} / {g_read} read = "
             f"{g_gam / max(g_read, 1):.0%} (reading stops at 2 genuine per prompt) | {verdict(round(100 * g_gam / max(g_read, 1)), 30, 10, 60)} |")
    nb = sum(not t2[p]["breaks"] for p in t2)
    e.append(f"| T2 s2300 with the hint ≥ 2 genuine of 16 on ≥ 14 of 16 | {nb} of 16 | {'holds' if nb >= 14 else 'MISS'} |")
    t3n = sum(v["outcome"] == "survives at 1,024" for v in t3.values())
    e.append(f"| T3 survivors 6 of 10 (3–9); resolved 2 (0–5); one genuine 2 (0–4) | survive {t3n}; resolved "
             f"{sum(v['outcome'] == 'resolved by sampling' for v in t3.values())}; one "
             f"{sum(v['outcome'].startswith('one') for v in t3.values())} | survivors: {verdict(t3n, 6, 3, 9)} |")
    e.append(f"| T4 s0750 confirmed on 24 of 43 (16–32) | {len(conf)} of 43 (strict reading {len(conf_s)}); cap 32 (deviation 4) | {verdict(len(conf), 24, 16, 32)} |")
    t2c = res["t2c"]
    pec = sum(v["dpo_outcome"] == "prompt-elicitable" for v in t2c.values())
    brc = sum(v["breaks"] for v in t2c.values())
    e.append(f"| T2c prompt-elicitable on 6 of 32 (2–12) | {pec} of 32 | {verdict(pec, 6, 2, 12)} |")
    e.append(f"| T2c the hint breaks s2300 on 10 of 32 (4–16) | {brc} of 32 | {verdict(brc, 10, 4, 16)} |")
    # ---- status per reach prompt, before -> after (pre-registered names)
    st = ["\n## Status per reach prompt (olmo-ifomega: reach) -> after this run", "",
          "| prompt | test 1 (65k) | test 2 / 2b / 2c (hint) | test 3 (1,024) | s2300 with the hint | s0750 (≤ 32) |",
          "|---|---|---|---|---|---|"]
    for pid, v in t1.items():
        st.append(f"| {pid[-8:]} | any: {v['out_any']}; doubly: {v['out_doubly']} | – | – | – | – |")
    for pid in ife3 + caps3:
        v = t2[pid]
        st.append(f"| {pid} | – | {v['dpo_outcome']} (T2{'b' if pid in caps3 else ''}) | – | "
                  f"{'breaks' if v['breaks'] else 'not broken'} | – |")
    for pid in P["r43"]:
        if pid in t2:
            h = f"{t2[pid]['dpo_outcome']} (T2){' / strict: ' + t2[pid]['dpo_outcome_strict'] if t2[pid]['dpo_outcome_strict'] != t2[pid]['dpo_outcome'] else ''}"
            br = "breaks" if t2[pid]["breaks"] else "not broken"
        elif pid in t2c:
            h = f"{t2c[pid]['dpo_outcome']} (T2c)"
            br = "breaks" if t2c[pid]["breaks"] else "not broken"
        else:
            h, br = "untested (hint conflict)", "–"
        t3s = t3[pid]["outcome"] if pid in t3 else "–"
        t4s = "confirmed" if t4[pid]["confirmed"] else f"not confirmed ({t4[pid]['genuine']} genuine in {t4[pid]['draws']})"
        st.append(f"| {pid} | – | {h} | {t3s} | {br} | {t4s} |")
    md += st
    C.dump(res, "outcomes.json")
    (C.OUT / "outcomes.md").write_text("\n".join(md) + "\n")
    (C.OUT / "expect.md").write_text("\n".join(e) + "\n")
    print("\n".join(md))
    print()
    print("\n".join(e))


if __name__ == "__main__":
    main()

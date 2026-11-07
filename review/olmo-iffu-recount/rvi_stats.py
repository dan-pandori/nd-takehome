"""Automatic (pre-hand-gate) statistics of run olmo-iffu from my re-grade (out/regrade/*.jsonl.gz).

Test 1: per prompt cut share at the new cap, finished-length quartiles / max, share longer than 32,768 tokens (cut
  at olmo-ifomega's cap), share with '</think>' inside the first 32,768 tokens, credits under omega / rl / any /
  doubly, and the same at the 32,768 truncation; 055 under the stored label 17.
Tests 2 / 2c: per prompt dpo strict k / 64 and s2300 strict k / 16, loose, answer words (median, share <= 60 by
  whitespace split) for all draws and for strict successes.
Test 3: per prompt strict / loose / cut over the 768 new draws; chunk coverage (stop rule).
Test 4: per prompt draws, chunks, strict per chunk (stop rule and the 32-draw cap).
-> out/stats.txt, out/stats.json
"""
import collections
import gzip
import json
import statistics as st

import rvi_core as C

LINES, RES = [], {}


def say(s=""):
    LINES.append(s)
    print(s)


def rows(job):
    return [json.loads(ln) for ln in gzip.open(C.OUT / "regrade" / f"{job}.jsonl.gz", "rt")]


def q(xs):
    xs = sorted(xs)
    if not xs:
        return None
    qs = st.quantiles(xs, n=4, method="inclusive") if len(xs) > 1 else [xs[0]] * 3
    return [round(qs[0]), round(qs[1]), round(qs[2]), max(xs)]


def short(pid):
    return pid.replace("omega_out_geometry_perpendicular_intersection_test_out_", "perp_")


def test1():
    say("## Test 1 (dpo, budget 65,536 - prompt tokens, 64 draws per prompt)")
    say("| prompt | n | cut at new cap | finished len q1/med/q3/max | > 32,768 tok | </think> by 32,768 | omega | rl | any | "
        "doubly | at 32,768 trunc: omega / rl / any | 055 omega @17 |")
    say("|---|---|---|---|---|---|---|---|---|---|---|---|")
    R = rows("T1_dpo")
    by = collections.defaultdict(list)
    for r in R:
        by[r["pid"]].append(r)
    res = {}
    for pid in sorted(by):
        rs = sorted(by[pid], key=lambda r: (r["chunk"], r["i"]))
        cut = sum(r["finish"] == "length" for r in rs)
        fin = [r["n_tok"] for r in rs if r["finish"] == "stop"]
        o = sum(r["omega"] for r in rs)
        rl = sum(r["rl"] for r in rs)
        an = sum(r["omega"] or r["rl"] for r in rs)
        db = sum(r["omega"] and r["rl"] for r in rs)
        to, tr = sum(r["t32_omega"] for r in rs), sum(r["t32_rl"] for r in rs)
        ta = sum(r["t32_omega"] or r["t32_rl"] for r in rs)
        over = sum(r["n_tok"] > 32768 for r in rs)
        te = sum(r["t32_think_end"] for r in rs)
        s17 = sum(bool(r.get("omega_stored_label")) for r in rs) if pid.endswith("055") else "–"
        cred = [{"chunk": r["chunk"], "i": r["i"], "n_tok": r["n_tok"], "finish": r["finish"], "omega": r["omega"],
                 "rl": r["rl"], "rl_main": r["rl_main"], "think_end": r["think_end"], "omega_ans": r["omega_ans"]}
                for r in rs if r["omega"] or r["rl"]]
        res[pid] = {"n": len(rs), "cut": cut, "fin_q": q(fin), "over32k": over, "think_end_32k": te, "omega": o,
                    "rl": rl, "any": an, "doubly": db, "t32": [to, tr, ta], "credited": cred,
                    "rl_main": sum(r["rl_main"] for r in rs)}
        say(f"| {short(pid)} | {len(rs)} | {cut} | {'/'.join(map(str, q(fin)))} | {over} | {te} | {o} | {rl} | {an} | "
            f"{db} | {to} / {tr} / {ta} | {s17} |")
    allr = R
    fin = [r["n_tok"] for r in allr if r["finish"] == "stop"]
    say(f"pooled: cut {sum(r['finish'] == 'length' for r in allr)} / {len(allr)}; finished median "
        f"{st.median(fin):,.0f} tokens (q {q(fin)}); > 32,768 tokens {sum(r['n_tok'] > 32768 for r in allr)} / "
        f"{len(allr)}; rl on the main thread (sympy live) adds {sum(r['rl_main'] and not r['rl'] for r in allr)}")
    for pid, v in res.items():
        say(f"   {short(pid)} credited draws: " + "; ".join(
            f"c{c['chunk']}.{c['i']} {c['n_tok']} tok {c['finish']} omega={int(c['omega'])} rl={int(c['rl'])} "
            f"think_end={int(c['think_end'])} ans={c['omega_ans'][:20]!r}" for c in v["credited"]))
    RES["test1"] = res


def if_table(title, jobs_dpo, jobs_s):
    say(f"\n## {title}")
    say("| prompt | dpo strict / n | dpo loose | dpo words med (≤ 60 share) | dpo strict-success words med | "
        "s2300 strict / n | s2300 words med (≤ 60 share) |")
    say("|---|---|---|---|---|---|---|")
    D = collections.defaultdict(list)
    S = collections.defaultdict(list)
    for j in jobs_dpo:
        for r in rows(j):
            D[r["pid"]].append(r)
    for j in jobs_s:
        for r in rows(j):
            S[r["pid"]].append(r)
    res = {}
    for pid in sorted(D, key=lambda p: (p.split("_")[0], int(p.split("_")[1]))):
        d, s = D[pid], S[pid]
        w = [r["answer_words"] for r in d if r["answer_words"] is not None]
        ws = [r["answer_words"] for r in s if r["answer_words"] is not None]
        sw = [r["answer_words"] for r in d if r["strict"]]
        res[pid] = {"dpo_n": len(d), "dpo_strict": sum(r["strict"] for r in d), "dpo_loose": sum(r["loose"] for r in d),
                    "dpo_words_med": st.median(w) if w else None, "dpo_le60": sum(x <= 60 for x in w) / max(len(d), 1),
                    "s_n": len(s), "s_strict": sum(r["strict"] for r in s),
                    "s_words_med": st.median(ws) if ws else None, "s_le60": sum(x <= 60 for x in ws) / max(len(s), 1),
                    "dpo_no_answer": sum(r["answer_words"] is None for r in d)}
        v = res[pid]
        say(f"| {pid} | {v['dpo_strict']} / {v['dpo_n']} | {v['dpo_loose']} | {v['dpo_words_med']} ({v['dpo_le60']:.2f}) | "
            f"{st.median(sw) if sw else '–'} | {v['s_strict']} / {v['s_n']} | {v['s_words_med']} ({v['s_le60']:.2f}) |")
    med_le80 = sum(1 for v in res.values() if v["dpo_words_med"] is not None and v["dpo_words_med"] <= 80)
    say(f"dpo median answer <= 80 words on {med_le80} of {len(res)} prompts; dpo draws without '</think>': "
        f"{sum(v['dpo_no_answer'] for v in res.values())}")
    return res


def test3():
    say("\n## Test 3 (dpo, 768 new draws per prompt, no hint)")
    R = rows("T3_dpo")
    by = collections.defaultdict(list)
    for r in R:
        by[r["pid"]].append(r)
    res = {}
    for pid in sorted(by, key=lambda p: int(p.split("_")[1])):
        rs = by[pid]
        ch = collections.Counter(r["chunk"] for r in rs)
        res[pid] = {"n": len(rs), "strict": sum(r["strict"] for r in rs), "loose": sum(r["loose"] for r in rs),
                    "cut": sum(r["finish"] == "length" for r in rs), "chunks": len(ch),
                    "chunks_full": sum(v == 16 for v in ch.values()), "chunk_range": [min(ch), max(ch)],
                    "no_answer": sum(not r["think_end"] for r in rs)}
        say(f"   {pid}: {res[pid]}")
    RES["test3"] = res


def test4():
    say("\n## Test 4 (s0750, fresh draws; stop at 2 strict per prompt, chunks of 16, cap 32 by the stop file)")
    by = collections.defaultdict(list)
    for j in ("T4_s0750", "T4b_s0750"):
        for r in rows(j):
            by[r["pid"]].append(r)
    res, viol = {}, []
    for pid in sorted(by, key=lambda p: int(p.split("_")[1])):
        rs = by[pid]
        perc = collections.defaultdict(lambda: [0, 0])
        for r in rs:
            perc[r["chunk"]][0] += 1
            perc[r["chunk"]][1] += r["strict"]
        chunks = sorted(perc)
        # sequential rule: chunk c+1 exists only if strict over chunks <= c is < 2 (T4); T4b is the hand continuation
        cum = 0
        for c in chunks[:-1]:
            cum += perc[c][1]
            if cum >= 2 and not any(r["job"] == "T4b_s0750" and r["chunk"] == c + 1 for r in rs):
                viol.append((pid, c))
        res[pid] = {"n": len(rs), "strict": sum(r["strict"] for r in rs),
                    "per_chunk": {c: perc[c] for c in chunks}, "jobs": sorted({r["job"] for r in rs})}
    say("   per prompt draws / strict: " + ", ".join(f"{p.split('_')[1]}:{v['n']}/{v['strict']}" for p, v in res.items()))
    say(f"   prompts with 16 draws (stopped at >= 2 strict in chunk 0): {sum(v['n'] == 16 for v in res.values())}; "
        f"32 draws: {sum(v['n'] == 32 for v in res.values())}; other: "
        f"{[(p, v['n']) for p, v in res.items() if v['n'] not in (16, 32)]}")
    say(f"   chunks submitted after >= 2 strict (outside the hand continuation): {viol if viol else 'none'}")
    RES["test4"] = res


def main():
    test1()
    RES["test2"] = if_table("Test 2 (hint; dpo 64, s2300 16)", ["T2_dpo"], ["T2_s2300"])
    RES["test2c"] = if_table("Test 2c (hint; dpo 64, s2300 16)", ["T2c_dpo"], ["T2c_s2300"])
    test3()
    test4()
    C.dump(RES, "stats.json")
    (C.OUT / "stats.txt").write_text("\n".join(LINES) + "\n")


if __name__ == "__main__":
    main()

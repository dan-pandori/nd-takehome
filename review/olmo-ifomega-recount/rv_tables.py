"""Markdown tables for review_olmo-ifomega.md, generated from out/*.json (no hand-copied numbers)."""
import json
import os

import rv_core as C


def f3(x):
    return f"{x:.3f}"


def iv(v):
    return f"{v[0]:.3f} [{v[1]:.3f}, {v[2]:.3f}]"


def passk_table(st):
    out = ["| task (prompts) | grade | model | samples | pass@1 [95 % CI] | pass@8 [95 % CI] | pass@16 |",
           "|---|---|---|---|---|---|---|"]
    for key, grades in (("ifbench|headline", ("strict", "loose")), ("ifbench|all", ("strict",)),
                        ("ifeval|headline", ("strict", "loose")), ("omega_out|headline", ("omega", "rl", "own"))):
        for g in grades:
            for m in ("dpo", "s0100", "s0750", "s2300"):
                r = st[key][g].get(m)
                if not r:
                    continue
                out.append(f"| {key.split('|')[0]} {key.split('|')[1]} ({st[key]['n_prompts']}) | {g} | {m} | {r['n_samples']} |"
                           f" {iv(r['pass@1'])} | {iv(r['pass@8'])} | {iv(r['pass@16']) if 'pass@16' in r else '–'} |")
    return "\n".join(out)


def ee_table(st):
    out = ["| task | grade | checkpoint | expected entries @8 [CI] | expected exits @8 [CI] | observed entries / exits (vs dpo's first 8) | (vs dpo's 16) |",
           "|---|---|---|---|---|---|---|"]
    for key, grades in (("ifbench|headline", ("strict",)), ("ifeval|headline", ("strict",)),
                        ("omega_out|headline", ("omega", "rl"))):
        for g in grades:
            for m, e in st[key][g]["entries_exits_k8"].items():
                a, b = e["expected_entries"], e["expected_exits"]
                out.append(f"| {key.split('|')[0]} | {g} | {m} | {a[0]} [{a[1]}, {a[2]}] | {b[0]} [{b[1]}, {b[2]}] |"
                           f" {e['observed_entries_k8']} / {e['observed_exits_k8']} | {e['observed_entries_vs_dpo16']} / {e['observed_exits_vs_dpo16']} |")
    return "\n".join(out)


def cand_table(st):
    out = ["| task | grade | \\|R\\| | reach (s2300 confirmed, dpo 0 in 256) | dpo resolved (≥ 2 in 256) | open | \\|V\\| | reverse | s2300 resolved | V open | verdict |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    for key, grades in (("ifbench|headline", ("strict", "loose", "rlview")), ("ifbench|all", ("strict",)),
                        ("ifeval|headline", ("strict", "loose")), ("omega_out|headline", ("omega", "rl", "doubly", "own"))):
        for g in grades:
            v = st[key][g]["verdict"]
            sc = v["status_counts"]
            rs = v["reverse_status"]
            op = sum(n for s, n in sc.items() if s.startswith("open"))
            out.append(f"| {key} | {g} | {len(st[key][g]['R'])} | {sc.get('reach', 0)} | {sc.get('dpo_resolved', 0)} |"
                       f" {op} ({', '.join(f'{s[5:]} {n}' for s, n in sc.items() if s.startswith('open'))}) |"
                       f" {len(st[key][g]['V'])} | {rs.get('reverse', 0)} | {rs.get('s2300_resolved', 0)} | {rs.get('open', 0)} |"
                       f" {v['verdict']} |")
    return "\n".join(out)


def len_table(st):
    out = ["| task | model | samples | mean tokens | cut at 32,768 | closes `</think>` |", "|---|---|---|---|---|---|"]
    for key in ("ifbench|all", "ifeval|headline", "omega_out|headline"):
        for m, l in st[key]["lengths_fixed"].items():
            out.append(f"| {key.split('|')[0]} | {m} | {l['samples']} | {l['mean_tok']:,} | {l['cut_share']:.4f} |"
                       f" {l['think_end_share']:.4f} |")
    return "\n".join(out)


def main():
    st = json.load(open(os.path.join(C.OUT, "stats.json")))
    print("### pass@k\n")
    print(passk_table(st))
    print("\n### entries / exits\n")
    print(ee_table(st))
    print("\n### candidates\n")
    print(cand_table(st))
    print("\n### lengths\n")
    print(len_table(st))


if __name__ == "__main__":
    main()

"""Prompt-level confirmation under the pre-registered prompt-specific rules 10 (ifbench_206), 11 (ifbench_207) and
12 (ifbench_268): olmo-ifladder's addendum says every item of such a prompt (all jobs) is confirmed under its rule.
Writes adjudicator task files ADJ4_<k>.txt with every read group of those prompts (one item file per group, its
reads and evidence), 10 per task; proposals are decided with rvc_confirm.py like the other rounds."""
import json

import rvc_hand as H
from rvc_core import SCR

PROMPTS = {"ifbench_206": 10, "ifbench_207": 11, "ifbench_268": 12}


def main():
    rd = H.reads()
    prompt = (H.HAND / "adjudicator_prompt.md").read_text().rstrip()
    items = [(g, rs) for g, rs in sorted(rd.items()) if g[0] in PROMPTS]
    groups, k = [], 0
    for p, rule in PROMPTS.items():
        its = [(g, rs) for g, rs in items if g[0] == p]
        for j in range(0, len(its), 10):
            b = its[j:j + 10]
            s = prompt + (f"\n\nAll items below answer the same prompt ({p}); apply rule {rule} to every one of them "
                          f"consistently, together with rules 1-9.\n\nItems:\n")
            for g, rs in b:
                s += f"\n- item file {SCR / 'items' / (rs[0][4] + '.md')} (item id {rs[0][4]}); readers:\n"
                for r in rs:
                    s += f"    - label {r[1]}, checker_agrees {r[2]}: {r[3][:500]}\n"
            s += f"\nOutput path: {SCR / 'adjud' / f'ADJ4_{k:02d}.json'}\n"
            (SCR / "tasks" / f"ADJ4_{k:02d}.txt").write_text(s)
            groups += [json.dumps(list(g)) for g, _ in b]
            k += 1
    json.dump(groups, open(H.HAND / "adj_ADJ4.json", "w"))
    print(len(groups), "groups in", k, "tasks", {p: sum(1 for g, _ in items if g[0] == p) for p in PROMPTS})


if __name__ == "__main__":
    main()

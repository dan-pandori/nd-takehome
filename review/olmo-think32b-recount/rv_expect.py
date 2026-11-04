"""Pre-registered expectations vs my recount (reviewer). Reads out/stats.json, out/stage0.json, out/ll_recount.json,
out/ext.json and my rows; prints one line per expectation with hit / miss."""
import gzip, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_core as C
S = json.load(open(os.path.join(C.HERE, "out", "stats.json"))); S0 = json.load(open(os.path.join(C.HERE, "out", "stage0.json")))
LL = json.load(open(os.path.join(C.HERE, "out", "ll_recount.json")))["summary"]
lines = []
def chk(name, val, lo, hi, point=None):
    ok = lo <= val <= hi
    lines.append(f"{'HIT ' if ok else 'MISS'} {name}: observed {val:.4g}; expected {point if point is not None else ''} ({lo}–{hi})")
exp1 = {"dpo": (0.62, 0.50, 0.74), "s0100": (0.64, 0.52, 0.76), "s0750": (0.67, 0.55, 0.78), "s2300": (0.71, 0.58, 0.82)}
exp8 = {"dpo": (0.85, 0.75, 0.93), "s0100": (0.86, 0.76, 0.94), "s0750": (0.87, 0.77, 0.94), "s2300": (0.88, 0.78, 0.95)}
for m in C.MODELS:
    chk(f"pass@1 rl {m}", S[f"pass@1_rl_{m}"][0], exp1[m][1], exp1[m][2], exp1[m][0])
    chk(f"pass@8 rl {m}", S[f"pass@8_rl_{m}"][0], exp8[m][1], exp8[m][2], exp8[m][0])
for m in C.MODELS:
    d = abs(S[f"pass@1_rl_{m}"][0] - S[f"pass@1_final_{m}"][0])
    lines.append(f"{'HIT ' if d <= 0.02 else 'MISS'} |final - rl| pass@1 {m}: {d:.4f} (expected <= 0.02)")
chk("s2300 - dpo pass@1 (rl)", S["dpass@1_rl_s2300-dpo"][0], 0.05, 0.12)
chk("s2300 - dpo pass@1 (final, not the pre-registered grade)", S["dpass@1_final_s2300-dpo"][0], 0.05, 0.12)
chk("dpo mean tokens (headline 59)", S["tokens_dpo"]["mean"], 10000, 20000, 14000)
chk("s2300 mean tokens (headline 59)", S["tokens_s2300"]["mean"], 10000, 22000, 15000)
for m in C.MODELS:
    chk(f"cut share {m}", S[f"tokens_{m}"]["cut_share"], 0.03, 0.15)
chk("entries k=8 (s2300 vs dpo, rl)", S["entries8_rl_s2300"][0], 2, 5)
chk("exits k=8 (s2300 vs dpo, rl)", S["exits8_rl_s2300"][0], 0.5, 2)
chk("|R|", len(S["R"]["union_of_sets"]), 1, 6, 3); chk("|V|", len(S["V"]["union_of_sets"]), 0, 3, 1)
E = json.load(open(os.path.join(C.HERE, "out", "ext.json")))
first_rl = next(h[0] for c in E["dpo|aime2025_28"] for h in c["hits"])
first_d = next(h[0] for c in E["dpo|aime2025_28"] for h in c["hits"] if h[1] == "D")
chk("dpo first rl success draw on the reach candidate", first_rl, 17, 256, 50)
chk("dpo first doubly success draw on the reach candidate", first_d, 17, 256, 50)
lines.append(f"{'HIT ' if LL['dpo_on_candidate']['share'] >= 0.75 else 'MISS'} LL: RL solutions inside dpo's own same-problem 2.5-97.5% range: {LL['dpo_on_candidate']['rl_inside']}/{LL['dpo_on_candidate']['rl_n']} (expected >= 75%; base n = {LL['dpo_on_candidate']['n_base']})")
lines.append(f"{'HIT ' if LL['dpo_reference']['share'] >= 0.75 else 'MISS'} LL (executor-style reference, other problems): {LL['dpo_reference']['rl_inside']}/{LL['dpo_reference']['rl_n']} (base n = {LL['dpo_reference']['n_base']})")
lines.append(f"{'HIT ' if abs(LL['dpo_on_candidate']['gap_rl_minus_base']) <= 0.1 else 'MISS'} LL mean per-token gap (RL - dpo same problem): {LL['dpo_on_candidate']['gap_rl_minus_base']:+.4f} nats (expected |gap| <= 0.1)")
# Stage 0
chk("Stage 0 dpo AIME 2024 pass@1 rl", S0["pass1_rl"], 0.55, 0.80); chk("Stage 0 dpo AIME 2024 pass@1 final", S0["pass1_final"], 0.55, 0.80)
rs0 = [r for r in C.rows() if r["job"] == "s0_dpo" and r["finish"] == "stop"]
boxed_any = 0
with gzip.open(os.path.join(C.ROOT, "artifacts/olmo32/samples/s0_dpo.jsonl.gz"), "rt") as f:
    for l in f:
        r = json.loads(l)
        if r["finish"] == "stop" and "\\boxed" in r["text"]:
            boxed_any += 1
lines.append(f"{'HIT ' if S0['uncut_think_end'] >= 0.95 else 'MISS'} Stage 0 uncut closing </think>: {S0['uncut_think_end']:.3f} (expected >= 0.95)")
lines.append(f"{'HIT ' if S0['uncut_boxed_after'] >= 0.95 else 'MISS'} Stage 0 uncut boxing an answer after </think>: {S0['uncut_boxed_after']:.3f} (expected >= 0.95); boxed anywhere: {boxed_any / len(rs0):.3f}")
lines.append(f"{'HIT ' if S0['rl_ne_final'] / S0['n'] <= 0.03 else 'MISS'} Stage 0 rl != final: {S0['rl_ne_final']}/{S0['n']} = {S0['rl_ne_final'] / S0['n']:.3f} (expected <= 0.03)")
lines.append(f"MISS/NA Stage 0 throughput: {S0['log_tok_per_s']:.0f} tok/s on 1 x H200 (expected 1,500-3,000 on 4 x A100 PCIe; different GPU)")
open(os.path.join(C.HERE, "out", "expectations.txt"), "w").write("\n".join(lines) + "\n")
print("\n".join(lines))

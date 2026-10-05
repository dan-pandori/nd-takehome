"""Record the manual verdicts for the 48 sampled claims (Task 4) and the manual resolutions of the 40 rows that the
population location heuristic could not confirm automatically (33 flags + 7 with no fragment located at >= 0.85).
Reader / id / quote / stated location are taken from s4_sample.json and s2_claims.json, not retyped.
match: exact = found after case/whitespace/unicode-quote/hyphenation normalisation (incl. alphanumeric-only match,
i.e. punctuation-only differences); markup = differs only by math markup in the source (e.g. tau vs \\tau);
paraphrase = wording differs; notfound; nosource.
Writes s4_verdicts.tsv and s4d_resolutions.tsv."""
import json

from common import OUT

sample = json.load(open(f"{OUT}/s4_sample.json"))
# k: (match, line(s) in source, location verdict OK/WRONG, note)
V = {
    1: ("exact", "258, 260", "OK", "Sec. 4 body text citing Fig. 5A/5C (Fig. 5 caption at 256); '>92%' is $>92\\%$ in source"),
    2: ("markup", "145", "OK", "source: 'temperature-only sampling at $\\tau=1.0$'; Sec. 2 Methodology"),
    3: ("markup", "308, 320", "OK", "2nd fragment is 'C^{\\prime}/C' in source; Sec. 2 Conceptual framework"),
    4: ("exact", "237 (psi def. 235)", "OK", "Sec. 3.3; Eqs. (3)-(5) at lines 248-268; psi formula matches (arguments omitted)"),
    5: ("exact", "352", "OK", "Sec. 4.1; beta-binomial likelihood = Eq. 15 (line 414)"),
    6: ("markup", "311", "OK", "formula claim (no quote): '-\\log(pass_D@k) ~ C Gamma(b) k^{-b}' inside Theorem 3.1 (line 295), Sec. 3"),
    7: ("exact", "105", "OK", "Sec. 2"),
    8: ("exact", "397", "OK", "Sec. 8 Discussion"),
    9: ("exact", "125", "OK", "Sec. 2; context 'informal account of model capabilities, as we are not aware of any rigorous accounts'"),
    10: ("exact", "71, 99", "OK", "found in both Sec. 1 and Sec. 2"),
    11: ("exact", "106", "OK", "Sec. 2"),
    12: ("exact", "512; 134", "OK", "Sec. 5.2.1 and Sec. 2.2 footnote 1"),
    13: ("markup", "283", "OK", "'$\\phi$ s'; Definition 5 (Reliability) in Sec. 3.1"),
    14: ("exact", "94; Eq. (1) at 125-129", "OK", "quote is footnote 1 of Sec. 2.1; Phi(pi,M,p) formula = Eq. (1)"),
    15: ("exact", "271", "OK", "Sec. 3.1"),
    16: ("exact", "385, 377", "OK", "under '4.1. Spurious failures'"),
    17: ("exact", "30 (.abs.txt)", "OK", "abstract-only source; Abstract"),
    18: ("exact", "40", "OK", "Abstract"),
    19: ("exact", "30 (.abs.txt)", "OK", "Abstract; 'Chinchilla 70B' confirmed"),
    20: ("exact", "80", "OK", "the line is the Figure 2 caption"),
    21: ("exact", "224, 225", "OK", "Sec. 7.1 next to Fig. 2 caption (222); 'held-out data' and 1,000 samples confirmed"),
    22: ("exact", "30 (.abs.txt)", "OK", "Abstract"),
    23: ("exact", "230", "OK", "Sec. 2.3"),
    24: ("exact", "951", "OK", "Sec. 6 Conclusion"),
    25: ("exact", "5123; caption 1119", "OK", "Sec. 5.7 + footnote 17 ('50% of the total weight'); Fig. 7 caption: anchor (20, 0), 50% weight"),
    26: ("markup", "172", "OK", "'$\\theta_{l}=0$'; Sec. 4.1"),
    27: ("markup", "259 (formula 255)", "OK", "Sec. 3.1; \\mathrm subscripts"),
    28: ("markup", "242, 286, 284", "OK", "Fig. 2 caption ('30-60 $\\times$') and Sec. 4.1; noise N(0, 0.01^2) confirmed"),
    29: ("exact", "1164", "OK", "Appendix D"),
    30: ("exact", "342, 346", "OK", "Sec. 4.3 and its footnote 3"),
    31: ("exact", "2154", "OK", "Sec. 5.2 (line 2148); PDF page 7 = printed p. 1146"),
    32: ("exact", "362", "OK", "Sec. 5; the '~' before 100 is lost in the text conversion, ledger marks it '[~]'"),
    33: ("exact", "1336", "OK", "Sec. 7"),
    34: ("exact", "231", "OK", "Assumption 2 in Sec. 4; 'within a small multiplicative factor like 1.1' confirmed"),
    35: ("exact", "507", "OK", "Sec. 3.1, page 9"),
    36: ("exact", "118", "OK", "Sec. 1"),
    37: ("exact", "133; 152", "OK", "Sec. 2.1; Chernoff-coefficient formulas and D_A <= 0.02 confirmed (no 2.2 heading before line 158)"),
    38: ("exact", "535", "OK", "Sec. 3.2.1, page 9"),
    39: ("exact", "1314", "OK", "Sec. 6; all numbers (0.0144, 0.0022, 5x10^10, 0.001, 0.07, 0.08, 0.12) confirmed"),
    40: ("exact", "394; 442-444", "OK", "Corollary 13 in Sec. 5.1.1; Sec. 7 item 1 supports the halving-theta paraphrase"),
    41: ("exact", "30 (.abs.txt)", "OK", "Abstract"),
    42: ("exact", "76", "OK", "Abstract"),
    43: ("markup", "256", "OK", "Sec. 3.1 (refers to its footnote 4) near Fig. 2; 3176 latents confirmed"),
    44: ("exact", "305; 297", "OK", "web headings '(5.2) Literal vs Isomorphic Models' (299) and '(5.1) Questions with Fresh Traction' (285)"),
    45: ("exact", "278", "OK", "Sec. 7"),
    46: ("exact", "135", "OK", "Sec. 1"),
    47: ("exact", "616; caption 562-566", "OK", "Sec. 3.5 says ranks 10 and 45; Table 1 caption says all PoS control-task probes rank 10: inconsistency real"),
    48: ("exact", "52; Table 1 at 114-182", "OK", "Abstract; Table 1 circuit 0.73 (Goat) / 0.72 (FLoat) vs full Llama-7B 0.66 confirmed"),
}
assert len(V) == len(sample) == 48
with open(f"{OUT}/s4_verdicts.tsv", "w", encoding="utf-8") as fh:
    fh.write("k\treader\tn\tid\tquote_abridged\tstated_location\tmatch\tline\tlocation\tnote\n")
    for k, r in enumerate(sample, 1):
        m, line, loc, note = V[k]
        q = r["claim"].replace("\t", " ")
        q = q if len(q) <= 110 else q[:107] + "..."
        fh.write(f"{k}\t{r['reader']}\t{r['n']}\t{r['pid'].split()[0]}\t{q}\t{r['loc']}\t{m}\t{line}\t{loc}\t{note}\n")

# ---- manual resolutions of the population location heuristic (s4d) flags and unlocated rows
R = [
    ("L2", 181, "consistent", "hit is method item '4. Relearning through Fine-tuning' inside Sec. 3 (lines 335-397)"),
    ("L4", 67, "consistent", "PDF page 1 = p. 1140, Sec. 1 (heading split across lines in PDF text)"),
    ("L4", 68, "consistent", "line 784 is Sec. 3 Methodology (p. 1143); 3PL Eq. 1 in Sec. 2.2"),
    ("L4", 69, "consistent", "PDF page 3 = p. 1142, Sec. 3 Methodology (line 304)"),
    ("L4", 70, "consistent", "PDF page 3 = p. 1142, Sec. 3"),
    ("L4", 71, "consistent", "PDF page 4 = p. 1143, Sec. 4 (instance analysis, heading ~line 638)"),
    ("L4", 72, "consistent", "PDF page 5 = p. 1144, between 4.1 and 4.2 (line 955)"),
    ("L4", 73, "consistent", "PDF page 5 = p. 1144, after '4.2 Understanding the guess parameter' (955), before Sec. 5 (1356)"),
    ("L4", 74, "consistent", "PDF page 6 = p. 1145, Sec. 5.1 (line 2106)"),
    ("L4", 75, "consistent", "PDF page 6 = p. 1145, Sec. 5.1"),
    ("L4", 76, "consistent", "PDF page 7 = p. 1146, Sec. 5.2 (line 2148)"),
    ("L4", 77, "consistent", "PDF page 8 = p. 1147, Sec. 6 Discussion (2327)"),
    ("L4", 78, "consistent", "PDF page 8 = p. 1147, Sec. 6"),
    ("L4", 79, "consistent", "PDF page 8 = p. 1147, Sec. 7 Conclusion (2379)"),
    ("L4", 147, "consistent", "page 18, under '7.1. DIF models'"),
    ("L5", 48, "consistent", "page 32, under '7.2 Summary of results' (1919-2024)"),
    ("L5", 49, "consistent", "page 32, Sec. 7.2"),
    ("L5", 50, "consistent", "page 33, Sec. 7.2"),
    ("L5", 68, "consistent", "lines 643/653 lie in 5.1 (582-1276); flag came from a table row read as a heading"),
    ("L5", 81, "consistent", "line 448 is item 3 of Sec. 7 (heading 438)"),
    ("L5", 127, "consistent", "TeX source: \\section{Introduction} (68)"),
    ("L5", 128, "consistent", "TeX source: Sec. 1"),
    ("L5", 129, "consistent", "TeX: \\subsection{Answering question 3} = 4.2 (456) and \\section{How Good is The Policy Found?} = Sec. 6 (589)"),
    ("L6", 119, "consistent", "web heading '(2) Crosscoder Basics' (75)"),
    ("L6", 120, "consistent", "web heading '(4.3) Model Diffing Sonnet Finetuning' (249)"),
    ("L6", 121, "consistent", "(4.3)"),
    ("L6", 122, "consistent", "(4.3)"),
    ("L6", 123, "consistent", "(4.3)"),
    ("L6", 124, "consistent", "(4.3)"),
    ("L6", 125, "consistent", "(4.3)"),
    ("L6", 126, "consistent", "(4.3)"),
    ("L6", 127, "consistent", "web heading '(4.2) What Kind of Comparisons are Possible?' (217)"),
    ("L6", 128, "consistent", "(5.2) at 299 and (5.1) at 285"),
    # rows with no fragment located at >= 0.85 by the heuristic (resolved by hand: markup differences)
    ("L1", 2, "consistent", "line 308 in 2.1; Eq. (1) at 316"),
    ("L1", 129, "consistent", "line 181 in 3.1 (3.2 heading follows)"),
    ("L4", 27, "consistent", "line 487 in Sec. 5"),
    ("L4", 94, "consistent", "line 200 in 3.4; Fig. 12 caption at 925"),
    ("L6", 68, "consistent", "line 95 in 3.1 ('$\\sim-13$ to $-8$')"),
    ("L6", 78, "consistent", "line 323 in Appendix C ('$\\sim 83\\%$')"),
    ("L6", 95, "consistent", "line 654 in 3.7 ('recovers $\\sim\\!20\\%$')"),
]
with open(f"{OUT}/s4d_resolutions.tsv", "w", encoding="utf-8") as fh:
    fh.write("reader\tn\tresolution\tnote\n")
    for a, b, c, d in R:
        fh.write(f"{a}\t{b}\t{c}\t{d}\n")
print("wrote s4_verdicts.tsv (48 rows) and s4d_resolutions.tsv", len(R), "rows")

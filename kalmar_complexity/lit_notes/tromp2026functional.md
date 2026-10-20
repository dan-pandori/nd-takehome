---
written_on: 2026-10-20
written_by: agent:claude (literature arm, kalmar-complexity)
papers:
  - tromp2026functional
---

# Tromp, "Functional Bits: Lambda Calculus based Algorithmic Information Theory"

Source: https://tromp.github.io/cl/LC.pdf. I read the version dated 24 September 2026 (20 pages, full text). It is the current form of Tromp's "Binary Lambda Calculus and Combinatory Logic" (2007). I also read https://tromp.github.io/cl/cl.html and the size comments in the source files of https://github.com/tromp/AIT (all 117 `.lam` files, fetched 2026-10-20).

## Paper claims (section / theorem numbers of the 2026 version)
- **Encodings.** BLC (Def. 2, §2.5): λM = `00`M, application MN = `01`MN, and de Bruijn index n (0-based) = `1^(n+1)0`. The 5 smallest closed terms are 4, 6, 7, 8 and 8 bits. BCL (Def. 3, §3.1): application = `1`, with K and S coded as `00` / `01`. The prose of §3.1 says "encode S as 00, K as 01", while Def. 3 and the worked example use K = `00`, S = `01`. The sizes are the same either way. "The size of a combinator with n K/S's … is 3n−1."
- **Interpreters.**
  - Thm 1: the BLC self-interpreter E is 206 bits. Footnote 1: "disproved in December 2025 … optimized the blc interpreter down to 170 bits". cl.html: "On September 21, 2026, Sean Palmer further optimized the interpreter to 168 bits and the universal machine to 190 bits". `ait/int.lam` ends `-- size 168 bits` and `ait/uni.lam` `-- size 190 bits`.
  - Thm 3: a CL interpreter written in λ (cross-interpreter F) is 119 bits.
  - Thm 4: the CL self-interpreter is 263 bits.
  - §3.2, the same F under bracket abstraction: 536 bits (basic rules), 281 (λ1), 275 (λ2), 263 (λ2 plus the 35-bit fixpoint Y″). For a term family X, λ1 gives 2,030 bits and λ2 gives 374.
  - "λ-calculus is a much more concise language than CL."
- **Universal machines (§4.1).** U = E⟨Ω⟩ is 232 bits (footnote: "since been optimized down to 190 bits"). U′ = F I is 272 bits.
- **Invariance (§4.3, Thm 5), "the first concrete instance of the Invariance Theorem, 2.1.1 in [Li & Vitányi, 2nd ed.]":** KS(x) ≤ KS′(x) + 125 and KP(x) ≤ KP′(x) + 125, where ′ denotes the CL machine. The other direction: "We state without proof that a redesigned U translates to a combinator of size 617".
- **Other description methods (§4).** Penrose's universal Turing machine is "5495 bits in size, over 26 times that of E". The Brainfuck self-interpreter has 423 instructions ≈ 1,269 bits. Levin wants measures whose mutual constants are "at most a few hundred bits".
- **Concrete bounds (§5).** KS(x) ≤ l(x) + 4. KP(x) ≤ l(x) + 326. KP(x,y) ≤ KP(x) + KP(y|x*) + 784, against Chaitin's LISP program for the same theorem: 2,872 bits.
- **§6:** "Sizes of constants in fundamental theorems are an indication, but one that is all too easily abused."

## Published sizes in the AIT repository (from source comments; scope as stated in each file)
| program | bits | file |
|---|---|---|
| BLC self-interpreter | 168 | ait/int.lam |
| BLC universal machine | 190 (178 non-strict) | ait/uni.lam |
| CL interpreter in λ (SK) | 236 (272 with Y) | ait/SKint.lam |
| Brainfuck interpreter | 830 ("this version is 4 bits shorter") | ait/bf.lam |
| prefix-delimiting (KP ≤ l+326) | 326 = 2 + 139 + 185 | ait/delimit.lam |
| sort binary lists (insertion; comment on `sort`) | 300 | lists/sort.lam |
| sort binary lists (radix-style, with I/O wrapper) | 436 | lists/sort2.lam |
| primes (characteristic sequence) | 167 | cl.html |
| Church numerals: multiplication / square / subtraction / sqrt | 19 / 16 / 56 / 118 | numerals/sqrt.lam |
| Church modulo / GCD / divisibility | 106 / 162 / 97 | numerals/*.lam |
| Fibonacci | 52 (74) | numerals/fib.lam |
| Ackermann | 63 | fast_growing.../ackermann.lam |
| Y combinator | 25 | ait/Y.lam |

`lists/reverse.lam` exists, but no size is stated. No size is stated for binary addition either (`numerals/binary_numerals.lam`). UNVERIFIED: whether "300 bits" on `sort` counts the let-bound helpers (`leq`, `insert`). The comment is placed on the `sort` binding.

## Our interpretation (for kalmar-complexity)
- The preregistration's encoding ("de Bruijn index i = 1^i 0") equals Tromp's `1^(n+1)0` if i is 1-based. Exact bit counts are comparable to the table above only if the run uses the same convention.
- The **BCL/BLC ratio depends on the bracket-abstraction algorithm**. F is 131 bits as defined; 119 bits after a beta reduction and a K→b substitution that Tromp avoids "because of its negative impact on bracket abstraction". For this interpreter the ratio is 263/(119–131) ≈ 2.0–2.2 with Tromp's rules and 536/(119–131) ≈ 4.1–4.5 with the basic rules. The preregistered "2.5 (1.5–4)" is therefore a statement about the abstraction rules as much as about the program. State the rules used.
- **Data encodings dominate small programs.** Multiplication is 19 bits on Church numerals but needs a binary-list algorithm otherwise. The run fixes encodings once (good), but its calibration numbers are only comparable to Tromp's where the encodings match.
- **Constants versus program sizes.** The BLC↔BCL constants (125 bits one way, ≤ 617 stated without proof the other) and the interpreter sizes of Turing-machine-like languages (1.3–5.5 kbits) are the same order as the ~10³–10⁴-bit programs the run compares.
  - For *minimal* lengths in Tromp's universal-machine sense (program bits fed to U), K_BCL(x) − K_BCL(y) ≥ K_BLC(x) − K_BLC(y) − (125 + 617). So a rank survives the language switch only if the BLC gap exceeds 742 bits.
  - This is a statement about K. Hand-written closed terms translated by bracket abstraction behave multiplicatively (ratio ≈ 2–4) instead.
- **Golfing effort is a real variable.** The self-interpreter went from 206 to 168 bits (−18 %) over 18 years of expert effort. The preregistration's "first passing version + one golfing pass" is the right stopping rule, but its numbers are upper bounds on K and may sit well above a golfed optimum.

## Limits
- Exact sizes are for one pair of languages. They do not calibrate Python. No published Python-in-BLC interpreter size was found, and the Python↔BLC constant is unknown.
- Sizes are upper bounds on K and are not minimal.

# Confirming rule for the OMEGA hand check of run olmo-iffu (written 2026-11-06 23:50 UTC, before any sample; NOT given to readers)

Problems: perp_055 (12-gon, answer 15), perp_068 (8-gon, 23), perp_069 (10-gon, 14). Reference sets of the
perpendicular, meeting pairs: `python3 olmo_iffu/label_check.py --pairs` (exact chord-angle rule and float geometry agree).

1. **sound**: the response's final count comes from (a) an explicit set of pairs equal to the reference set, or (b) a
   valid counting rule (coordinates / slopes / chord-angle criterion, plus an intersection test that admits interior
   crossings and shared endpoints) executed without an error the count depends on. Slips corrected later are fine.
2. **flawed**: the official count is reached from a set that differs from the reference set (missing and extra pairs
   cancel), or a perpendicularity / meeting decision the count depends on is wrong or assumed.
3. **guess**: the number is not derived: stated after abandoned or truncated work, extrapolated, or chosen among
   candidates without the enumeration that decides it.
4. A response credited only inside its thinking (cut at the cap, or stopping before its write-up) is judged on the
   derivation that reaches the credited answer; `where` records that it is think-only.
5. Reader labels are confirmed against 1–3 by checking the response's counted pairs against the reference list; a
   disagreement goes to a second blinded reader before I decide, and both labels are kept in the table.

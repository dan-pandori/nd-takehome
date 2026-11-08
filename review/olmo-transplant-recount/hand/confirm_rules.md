# My adjudication rules (written 2026-11-08T09:41:13Z, after A and part of B, before any C label)

1. The final label of an item is the majority of my blinded readers (A; B when read; C on every A/B split).
2. I override a majority only when its deciding observation is a factual error about the answer that I can check
   mechanically (a miscount, a misquoted word, a constraint the answer verifiably meets or misses), and I record the
   check in hand/confirm.json. Judgement calls (is a fragment answer "substantive", is a keyword list "stuffing")
   stay with the majority.
3. format:sub-bullets answers whose "sub-bullets" are inline " - " clauses (no line starting with "-" under a "*"
   line): the official checker passes them (it only looks for any "-" after each "*"). My readers' labels stand; I do
   not override in either direction. Because olmo-ifomega's source labels count some such answers genuine, I report a
   mechanical sensitivity instead (rvt_rates mode with the natural reading: such successes counted gamed).
4. Every item where my final label differs from the executor's is listed in out/hand.txt with all readers' evidence.

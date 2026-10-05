# Executor's independent re-check of the readers' claims (run capability-defs)

Method: random rows drawn from each reader's `_claims_<TAG>.md` (`shuf --random-source=<(yes 42)`), each phrase
searched again with `capability_defs/lit/quote.py` in the reader's fetched text (`~/cd_sources/`). V = found verbatim
(up to whitespace / math markup) at the stated location; X = not found or wrong location.

| # | reader | id | claim (abridged) | stated location | found at | status |
|---|---|---|---|---|---|---|
| 1 | L1 | 2407.21787v3 | "these laws are not as exact as training scaling laws" | Sec. 3.1 | 3.1 Scaling Laws for Repeated Sampling | V |
| 2 | L1 | 2502.17578v1 | "selection bias … power law scaling are more likely to garner more interest" | Sec. 7 | 7 Discussion and Future Directions | V |
| 3 | L1 | 2310.03262v3 | "not captured by conventional evaluation strategies due to insufficient measurement resolution" | Abstract | abstract (line 70) | V |
| 4 | L1 | 2509.24012v2 | "the compute law predicts slightly worse for small k and the gold reference law … large k" | Abstract | abstract (line 57) | V |
| 5 | L1 | 2407.21787v3 | "With unlimited samples, any model that assigns a non-zero probability to every sequence will achieve perfect coverage" | Sec. 1 | 1 Introduction | V |
| 6 | L1 | 2510.05197v1 | RLVR "training on difficult problems requires correctly sizing batches …" | Sec. 1.1 | 1.1 Contributions | V |
| 7 | L1 | 2510.05197v1 | "Ground truth estimates are computed for pass@k using all 10,000 available samples" | Sec. 5.1 | 5.1 Experimental Setup (text has `10\,000`; found after normalising the LaTeX thin space) | V |

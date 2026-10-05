"""Controls for the s4 matcher: a verbatim quote must be 'exact'; mutated / fabricated quotes must not be."""
import sys
sys.argv = [sys.argv[0], "none"]          # do not run the sample
import s4_reverify as M
S = M.Source("2407.21787.txt")
tests = [
 ("positive: verbatim", "With unlimited samples, any model that assigns a non-zero probability to every sequence will achieve perfect coverage"),
 ("positive: case+curly quotes+dash", "WITH unlimited samples, any model that assigns a non–zero probability to every sequence will achieve perfect coverage"),
 ("negative: one word changed", "With unlimited samples, any model that assigns a non-zero probability to every sequence will achieve imperfect coverage"),
 ("negative: number changed", "we observe that coverage grows with the number of samples over five orders of magnitude"),
 ("negative: fabricated", "Repeated sampling proves that reinforcement learning creates new capabilities in every model family"),
]
for name, q in tests:
    print(name, "->", S.search(q)[0])
S2 = M.Source("2510.05197.txt")
print("positive: LaTeX thin space 10\\,000 ->", S2.search("Ground truth estimates are computed for pass@k using all 10,000 available samples")[0])
print("negative: 1,000 instead of 10,000 ->", S2.search("Ground truth estimates are computed for pass@k using all 1,000 available samples")[0])

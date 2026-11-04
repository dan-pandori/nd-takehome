# Vendored graders (unmodified copies; licences alongside)

| directory / file | source | commit |
|---|---|---|
| `ifbench/` (`__init__.py`, `instructions.py`, `classic_instructions.py`, `instructions_registry.py`, `instructions_util.py`) | github.com/allenai/IFBench `ifbench/` | `cd189a9c2889526d8af901d2103fd3e1ffcea6df` (2026-11-02) |
| `ifbench_evaluation_lib.py` | the same repo's top-level `evaluation_lib.py` (renamed only, so it does not clash with IFEval's module of the same name) | same |
| `instruction_following_eval/` (`evaluation_lib.py`, `instructions.py`, `instructions_registry.py`, `instructions_util.py`) | github.com/google-research/google-research `instruction_following_eval/` (the official IFEval checker) | `e6890f85757dd84e27ca6df2dd30651dafad28e0` (2026-07-22; only type-checker comments since `c27ed001`, 2025-06-03) |

`ifbench/data/IFBench_test.jsonl` at that commit equals `allenai/IFBench_test` @ `ed7c1245` on every key, prompt,
instruction list and kwargs (the repo's older top-level `data/IFBench_test.jsonl` differs on keys 13 and 19).
`olmo_ifomega/grade.py` calls each package's own `test_instruction_following_strict` / `_loose`.

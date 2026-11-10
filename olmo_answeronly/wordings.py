"""The registered changes of run olmo-answeronly (pre-registration preregistration/olmo-answeronly.md). Fixed before
any sample; not tuned. Token ids from olmo_answeronly/tok_enc.py (torch-free; re-checked on the pod against the HF
tokenizer by sample_prefix.py's --check_wordings)."""

A1 = "After thinking, reply with only your final answer, exactly as drafted, with no introduction or explanation."
A2 = "Answer in at most 60 words."  # olmo_iffu/build_problems.py HINT, verbatim
USER_JOIN = "\n\n"                  # olmo_iffu/build_problems.py: prompt_sample = prompt + "\n\n" + HINT
USER_SUFFIX = {"A1": USER_JOIN + A1, "A2": USER_JOIN + A2}

A3 = "I will now output exactly the final draft above and nothing else."
A3_TEXT = A3 + "\n"  # a line of its own: the stored token before `</` always ends in "\n"; then the stored closing
A3_IDS = [40, 690, 1457, 2612, 7041, 279, 1620, 10165, 3485, 323, 4400, 775, 627]

A4_K = 5  # prefill = the first min(5, n - 1) of the n stored answer ids after `</think>` (EOS excluded): never all of it

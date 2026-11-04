"""Import open-instruct's real ground_truth_utils.py / math_utils.py (7e780f2fea, unmodified copies in upstream/)
through stub modules for the parts MathVerifier never touches (litellm, IF functions, judge prompts, logger).
Reviewer code (olmo-think32b review); independent of olmo32/grade.py."""
import asyncio
import os
import shutil
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.join(HERE, "upstream")


def _build_pkg():
    d = tempfile.mkdtemp(prefix="oi_pkg_")
    p = os.path.join(d, "open_instruct")
    os.makedirs(os.path.join(p, "IFEvalG"))
    shutil.copy(os.path.join(UP, "7e78_open_instruct_ground_truth_utils.py"), os.path.join(p, "ground_truth_utils.py"))
    shutil.copy(os.path.join(UP, "7e78_open_instruct_math_utils.py"), os.path.join(p, "math_utils.py"))
    stubs = {
        "__init__.py": "",
        "logger_utils.py": "import logging\ndef setup_logger(name=None):\n    return logging.getLogger(name)\n",
        "if_functions.py": "IF_FUNCTIONS_MAP = {}\n",
        "IFEvalG/__init__.py": "",
        "IFEvalG/instructions_registry.py": "INSTRUCTION_DICT = {}\n",
        "judge_utils.py": "EXTRACTOR_MAP = {}\nJUDGE_PROMPT_MAP = {}\nPRICE_PER_TOKEN = {}\n"
                          "def build_messages(*a, **k):\n    raise RuntimeError('stub')\n",
        "utils.py": "def extract_final_answer(x):\n    return x\n",
    }
    for k, v in stubs.items():
        with open(os.path.join(p, k), "w") as f:
            f.write(v)
    lit = types.ModuleType("litellm")

    async def acompletion(*a, **k):
        raise RuntimeError("stub")
    lit.acompletion = acompletion
    sys.modules.setdefault("litellm", lit)
    sys.path.insert(0, d)
    return d


_build_pkg()
from open_instruct import ground_truth_utils as gtu  # noqa: E402
from open_instruct import math_utils as mu  # noqa: E402

# the files imported are byte-identical to upstream/ (checked by the caller via sha256)
VERIFIER = gtu.MathVerifier()


def rl_grade(text: str, label: str) -> bool:
    """The RL path: VerifierFunction.async_call -> loop.run_in_executor(None, __call__) (a worker thread)."""
    async def go():
        return await VERIFIER.async_call(tokenized_prediction=[], prediction=text, label=label, query=None)
    return asyncio.run(go()).score > 0


def main_grade(text: str, label: str) -> bool:
    """Diagnostic: __call__ on the main thread (signal timeout installable, sympy is_equiv live)."""
    return VERIFIER(tokenized_prediction=[], prediction=text, label=label).score > 0


if __name__ == "__main__":
    import hashlib
    for f in ("ground_truth_utils.py", "math_utils.py"):
        a = hashlib.sha256(open(os.path.join(os.path.dirname(gtu.__file__), f), "rb").read()).hexdigest()
        b = hashlib.sha256(open(os.path.join(UP, "7e78_open_instruct_" + f), "rb").read()).hexdigest()
        print(f, a == b, a[:16])
    # unit checks: each must print the expected value
    print(rl_grade("so the answer is \\boxed{70}", "70"), "expect True")
    print(rl_grade("so the answer is \\boxed{71}", "70"), "expect False")
    print(rl_grade("\\boxed{70} ... later \\boxed{71}", "70"), "expect False (last boxed only)")
    print(rl_grade("\\boxed{\\dfrac{140}{2}}", "70"), "expect False on RL path (sympy dead)")
    print(main_grade("\\boxed{\\dfrac{140}{2}}", "70"), "expect True on main thread (sympy live)")

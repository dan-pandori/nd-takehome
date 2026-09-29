#!/bin/sh
# Point git at ci/hooks (run repo-hygiene-2). core.hooksPath is shared by every worktree of the clone; a branch without
# ci/hooks/ simply has no hooks, so older run branches are unaffected.
git config core.hooksPath ci/hooks && echo "core.hooksPath = ci/hooks (pre-commit: ci/check_sizes.sh)"

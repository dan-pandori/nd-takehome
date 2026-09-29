#!/bin/sh
# Install the CI workflow (run repo-hygiene): GitHub refuses a push that adds .github/workflows/* unless the token has
# the `workflow` scope, which the VPS's token did not have on 2026-09-29. Once it does
# (`gh auth refresh -h github.com -s workflow`), run this on the branch to be pushed (normally `dan`).
set -e
cd "$(dirname "$0")/.."
mkdir -p .github/workflows
git mv ci/ci.yml .github/workflows/ci.yml
sed -i 's|^# GitHub Actions workflow (run repo-hygiene). Lives in .github/workflows/ci.yml; see ci/install_workflow.sh.|# GitHub Actions workflow (run repo-hygiene): the steps are in ci/run_ci.sh.|' .github/workflows/ci.yml
git add .github/workflows/ci.yml
git commit -m "ci: install the GitHub Actions workflow (ci/install_workflow.sh)"
git push

#!/bin/bash
# Publish changed files to the papi-bank GitHub repo.
# Git-over-HTTPS is not available here, so this pushes through the GitHub
# REST API (blobs -> tree -> commit -> ref). The CI workflow rebuilds the
# Pages site on every new commit to main.
#
# Usage: tools/publish.sh "commit message" [repo/path ...]
# Defaults to the two account CSVs.
set -euo pipefail
cd "$(dirname "$0")/.."

msg="${1:-Update account CSVs}"
if [ $# -gt 0 ]; then shift; fi
files=("$@")
if [ ${#files[@]} -eq 0 ]; then
  files=(data/alejandro.csv data/juliana.csv)
fi

args=()
for f in "${files[@]}"; do
  args+=("$f:$f")
done

python3 ~/workspace/skills/github/bin/gh-push.py \
  alexrecarey/papi-bank main "$msg" "${args[@]}"

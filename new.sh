#!/usr/bin/env bash
# Git Bash version of new.cmd:  ./new.sh <problem-url>
cd "$(dirname "$0")"
for py in "py -3" python3 python; do
  if $py --version >/dev/null 2>&1; then exec $py tools/ps.py new "$@"; fi
done
echo "Python not found."

# Problem Solving

My C++ solutions from Codeforces, LeetCode, VJudge training and other judges, all in one repo.

Progress, reviews and notes live in **Notion → Second Brain → Problem Solving**. This repo only holds the code.

## Structure

```
codeforces/   1352A.cpp
leetcode/     0001-two-sum.cpp
atcoder/      abc300_c.cpp
cses/         1068.cpp
other/        <judge>-<id>.cpp
templates/    template.cpp, leetcode.cpp, contest_review.md
tools/        ps.py (new / listen / sync), git hook
docs/         workflow.md, recurring-mistakes.md
archive/      old repos, kept as they were (see below)
```

## Setup (once)

1. Install the **Competitive Companion** browser extension.
2. Run `setup.cmd`. It sets up git, saves your Notion token to `.env` (never committed), and starts the click listener, which also runs at every Windows login.

## Start a problem

- **From the browser:** on the problem page, click the Competitive Companion button (green +). The file is created in the right folder with the samples in `input.txt`, and VS Code opens it.
- **From the terminal:** `.\new <problem-link>` (or `./new.sh <link>` in Git Bash).

If the file already exists, you get a warning: check Notion before solving it again.

## The footer (bottom of every file)

```cpp
// ------------------------------------------------------------
// CF-1352A — Sum of Round Numbers
// https://codeforces.com/problemset/problem/1352/A
// Sources: saad, icpc
// Went:    struggled          (easy | struggled | hint | editorial)
// Insight: each non-zero digit × its place value is one round number
```

**Fill it in, then commit. The git hook logs the problem in Notion automatically:** rating and tags from Codeforces/LeetCode, the review date, and the GitHub link.
Short names work in Sources: `saad`, `icpc`, `contest`, `daily`.
To commit without logging, put `[skip notion]` in the commit message.

## Rules

- **Each problem has one file**, named by its original judge ID. Problems from VJudge go in the folder of their original judge.
- **A re-solve overwrites the file.** Committing it again counts as a review in Notion. Git history keeps the old version.

## Commit messages

```
CF-1352A: solved
LC-1: re-solved (review 2)
```

## Archive

`archive/` holds the solutions from my old repos (`codeforces`, `vjudge`, `daily-leetcode`, `CPOS`) in their original folder layout. Most of them don't record a judge ID, so they can't be renamed safely.

- When an old problem comes up again, re-solve it and save the new file in the right top-level folder. The archive copy can stay where it is.
- Don't add new files to `archive/`.

LeetCode solutions whose problem number was known were moved straight into `leetcode/`.

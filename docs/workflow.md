# Workflow

Adapted from my CPOS workflow. The goal is improvement, not just getting Accepted.

## Before coding
1. **Create the file** (Competitive Companion click or `.\new <link>`). If it warns that the file already exists, follow the overlap rule on the Notion Problem Solving page.
2. **Read the whole statement without touching the keyboard.** Make sure you understand the goal, the input, the output and the constraints.
3. **Predict.** What topic is it? How hard is it? Have I seen something like it before?

## Solving
4. **Think on your own first.** Draw examples, test small cases, use pen and paper.
5. **Design it in words before writing code.** Why does it work? What's the complexity? If you can't justify it, keep thinking.
6. **Ask for help gradually, and only if you're stuck:** observation → hint → strong hint → algorithm → full solution. Never skip straight to the solution.
7. **Implement** from `templates/template.cpp`. Aim for correct and simple.

## Debugging (before asking anyone)
8. Check edge cases, overflow, off-by-one errors, indexing, empty input and n = 1. See `recurring-mistakes.md`.

## After Accepted
9. **Fill in the footer** at the bottom of the file: Sources, Went, Insight. Longer notes and drafts go in the problem's Notion page.
10. **If a mistake shows up again,** add it to `recurring-mistakes.md`. Write the principle ("verify prefix-sum indexing"), not the incident ("forgot line 27").
11. **Commit:** `CF-1352A: solved`. The hook logs it in Notion.

## Rules
- AI is a mentor, not a replacement for thinking.
- Struggle productively. Learn instead of memorizing.
- Finish a problem before moving on.

# Recurring Mistakes

## Off-by-One Errors

Occurrences: 0

Description

I frequently make indexing mistakes, especially when converting between 0-based and 1-based indexing.

How to Prevent

- Draw indices.
- Test n = 1.
- Test first and last element.

---

## Overflow

Occurrences: 0

Description

I occasionally forget to use long long.

How to Prevent

- Check constraints first.
- Estimate maximum possible values before coding.

---

## Incorrect Greedy Assumption

Occurrences: 0

Description

Sometimes I assume a greedy choice is correct without proving it.

How to Prevent

- Try to construct a counterexample.
- Think about an exchange argument.

---

## Ignoring Edge Cases

Occurrences: 0

Description

I sometimes validate only normal cases.

How to Prevent

Test:

- Empty
- Single element
- Maximum constraints
- Duplicate values
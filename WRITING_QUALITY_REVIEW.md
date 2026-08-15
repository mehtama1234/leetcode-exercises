# Writing Quality Review

Review date: 2026-08-15

## Result

The problem READMEs match the current teaching standard.

- 140 problem READMEs were checked.
- Every problem README has at least two `diagram` blocks.
- The remaining banned filler words from `scripts/REWRITE_SPEC.md` were removed.
- The exemplar style is still anchored by `02-arrays-hashing/0001-two-sum/README.md`.

## What Good Looks Like Here

Each explanation should start from the real question, then show the slow idea, the
wasted work, and the smaller idea that removes that waste.

```diagram
problem -> slow honest try -> repeated work -> remembered state -> faster answer
```

The diagrams should teach with a tiny example. They should show state changing,
not decorate the page.

```diagram
index:   0    1    2    3
nums:  [ 2,   7,  11,  15 ]     target = 9
seen:  {}
step:  x=7 needs 2 -> 2 was seen at index 0
```

## Guardrail

Keep enforcing `scripts/REWRITE_SPEC.md`: plain everyday words, no hype, no filler,
and no technical term unless it is explained in a few words the first time it is
used.

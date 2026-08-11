# Rewrite spec — plain words, first principles, real diagrams

You are rewriting the `README.md` for each assigned problem. **Do not touch
`solution.py`.** Keep the same section headings and order. The goal is a clearer,
warmer, more visual explanation.

**Read the gold-standard example first and match its voice and its diagram style
exactly:** `02-arrays-hashing/0001-two-sum/README.md`.

## Voice
- Simple, everyday words. Short sentences. Explain it the way you'd explain it to a
  sharp friend who hasn't seen the trick yet.
- Build from first principles: start from what is actually being asked, show the
  obvious slow idea, point at the *specific waste* in it, and let the fast idea
  fall out of removing that waste. Don't just announce the trick.
- Tie it to the big picture: name the one reusable idea the problem teaches
  (trading memory for speed, precomputing once, keeping an invariant true, splitting
  a problem in half, using sorted order, remembering instead of re-searching…) and,
  in "Why this matters", where that idea shows up in real systems.

## Banned — clichés and filler (do not use)
"at the end of the day", "under the hood", "the name of the game", "bread and
butter", "dive in", "deep dive", "in a nutshell", "the magic", "elegant",
"powerful", "robust", "seamless", "leverage", "utilize", "simply", "obviously",
"clearly", "trivially", "of course", "needless to say", "it turns out that",
and filler "just"/"basically"/"essentially". No hype. No motivational fluff.

## Jargon rule
If a technical term is truly needed (invariant, memoization, amortized, DAG,
in-place), give a 3–6 word plain gloss the first time you use it. Prefer the plain
phrasing outright — say "each item is pushed and popped at most once, so the total
work stays linear" instead of "amortized O(1)". Big-O is allowed but always restate
it in words too ("about n steps"; "doubling the input roughly quadruples the work").

## Diagrams — REQUIRED (this is the main upgrade)
Include **at least two** fenced blocks using the language tag `diagram`:

    ```diagram
    ...ascii picture here...
    ```

These render as a distinct "whiteboard" panel. Rules:
- Use plain ASCII: letters, digits, `| - + _ = / \` and arrows `-> <- ^ v`.
  Box-drawing chars like `└ ┘ ▲` are okay in moderation but keep it portable.
- Tie every diagram to a tiny concrete example (small array, small tree, a few steps).
- Prefer a **worked trace** over a decoration: show the state changing step by step.
- Match the diagram to the problem shape:
  - arrays / two pointers / sliding window → index row + markers moving across steps
  - linked list → `node -> node -> node` with the pointer rewiring drawn
  - trees / graphs → draw the little tree or graph
  - dynamic programming → draw the table and show a couple of cells filling, with
    arrows to the cells they depend on
  - stack / queue / heap → show the contents growing and shrinking step by step
- Keep each diagram small and correct. A wrong diagram is worse than none.

## Keep
- The section set: `# N. Title`, the bold Pattern/Difficulty/Link lines,
  `## The problem in plain words`, `## Why this matters`, `## Start from the obvious`,
  `## Find the waste` and/or `## The insight`, `## Complexity`, `## Pitfalls`,
  `## Transfer`. (A problem may keep an extra section it already has.)
- Correct facts and complexity. Keep the real sibling links in Transfer.
- Reasonable length — clearer, not padded.

## Rules
- Rewrite only the `README.md` files in your assigned folders. Never edit `solution.py`.
- Do not run git.
- Report which problems you rewrote and how many diagrams each got.

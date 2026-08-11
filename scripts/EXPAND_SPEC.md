# Expansion spec — implement each problem end to end (read fully first)

You are adding solutions to a first-principles LeetCode teaching repo at
`/home/manishmehta/ui-projects/leetcode-exercises/`.

**Read the exemplar first and match its style and depth exactly:**
- `02-arrays-hashing/0001-two-sum/solution.py`
- `02-arrays-hashing/0001-two-sum/README.md`  (note its section order, including
  the `## Why this matters` section — every problem must have one)

For **each** assigned problem, create two files in the given folder (already exists):

## `solution.py`
- Module docstring: `"""N. Title — <leetcode url>"""` then a 1–2 line plain restatement.
- Correct, clean, **type-annotated**, **self-contained and runnable** Python. Define
  any helper types the problem needs inside the file (`ListNode`, `TreeNode`, a
  graph `Node`, etc.) plus small build/serialize helpers so tests run standalone.
- For class-design problems use the exact LeetCode class name (`LRUCache`,
  `MinStack`, `Twitter`, `TimeMap`, `RandomizedSet`, `LFUCache`, `NumArray`,
  `MedianFinder`, `Trie`, `Codec`, etc.).
- When genuinely instructive, show the **naive** approach AND the **optimal** one
  as separate named functions with docstrings explaining *why* (mirror
  `two_sum_brute` vs `two_sum`). For simple problems one clean function is enough.
- End with a `_test()` running the official LeetCode example cases **plus 1–2 edge
  cases** as `assert`s, printing `"<short_name>: all cases passed"`, guarded by
  `if __name__ == "__main__": _test()`.
- **It must actually run.** Execute `python3 solution.py` in the problem folder and
  fix until it exits 0 and prints the passed line. Mandatory — unverified doesn't count.

## `README.md` (first-principles, plain everyday words, no jargon dumps)
Use this exact section order:
- `# N. Title`
- `**Pattern:**`, `**Difficulty:**`, `**Link:**` (bold lines)
- `## The problem in plain words`
- `## Why this matters` — 2–4 tight paragraphs (~120–200 words): the deeper
  operation this stands for; 2–4 **concrete, honest** real-world places the pattern
  shows up (real systems/products/engineering tasks — no hand-wavy "used
  everywhere"); and what resource the good solution buys (time, memory, one pass
  over an un-rewindable stream, avoiding a costly recompute, a latency budget).
- `## Start from the obvious` — the brute/naive idea as a short code sketch, why it's the honest first thought
- `## Find the waste` and/or `## The insight` — **derive** the optimal idea from what the brute force repeats or throws away
- `## Complexity` — time and space **with reasoning**
- `## Pitfalls` — real edge cases and common mistakes
- `## Transfer` — the reusable pattern and 1–3 sibling problems

Keep it concrete and honest. Use fenced code blocks for sketches.

## Rules
- Only write inside your assigned problem folders. Do **not** touch other files.
- Do **not** run git.
- Report which problems you finished and confirm each one's test passed.

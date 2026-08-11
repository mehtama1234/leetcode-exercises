# Implementation spec (read before writing anything)

You are adding solutions to a first-principles LeetCode teaching repo at
`/home/manishmehta/ui-projects/leetcode-exercises/`.

**First, read the exemplar and match its style and depth exactly:**
- `02-arrays-hashing/0001-two-sum/solution.py`
- `02-arrays-hashing/0001-two-sum/README.md`

For **each** assigned problem you will create two files at the given folder
(the folder already exists):

## `solution.py`
- Module docstring: `"""N. Title — <leetcode url>"""` then a 1–2 line plain
  restatement of the task.
- Correct, clean, **type-annotated** Python (`from typing import List, Optional, Dict`).
- **Self-contained and runnable.** Define any helper types the problem needs
  inside the file so it runs standalone:
  - linked list → a `ListNode` class + a `build_list`/`to_list` helper for tests
  - trees → a `TreeNode` class + a builder from a level-order list
  - clone graph → a `Node` class
- For class-design problems, use the exact class name LeetCode uses
  (`Trie`, `WordDictionary`, `MedianFinder`, `Codec`, `Solution` where relevant).
- When genuinely instructive, show the **naive** approach AND the **optimal** one
  as separate named functions, each with a docstring explaining *why*
  (mirror `two_sum_brute` vs `two_sum`). For simple problems, one clean function
  is enough — don't pad.
- End with a `_test()` that runs the official LeetCode example cases **plus 1–2
  edge cases** as `assert`s, prints `"<short_name>: all cases passed"`, guarded by
  `if __name__ == "__main__": _test()`.
- **It must actually run.** Execute `python3 solution.py` in the problem folder and
  fix until it exits 0 and prints the passed line. This is mandatory — a solution
  that isn't verified doesn't count.

## `README.md` (first-principles, plain everyday words, no jargon dumps)
Follow the exemplar's shape:
- `# N. Title`
- Bold lines: `**Pattern:**`, `**Difficulty:**`, `**Link:**`
- `## The problem in plain words`
- `## Start from the obvious` — the brute/naive idea as a short code sketch, and
  why it's the honest first thought
- `## Find the waste` and/or `## The insight` — **derive** the optimal idea from
  what the brute force repeats or throws away; don't just assert the trick
- `## Complexity` — time and space **with reasoning**
- `## Pitfalls` — real edge cases and common mistakes
- `## Transfer` — the reusable pattern and 1–3 sibling problems it applies to

Keep it concrete and honest. Use fenced code blocks for sketches.

## Rules
- Only write inside your assigned problem folders. Do **not** touch other files.
- Do **not** run any git commands.
- Report back which problems you finished and confirm each one's test passed.

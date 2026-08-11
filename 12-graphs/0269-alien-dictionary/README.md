# 269. Alien Dictionary

**Pattern:** Build a graph from ordering hints + topological sort
**Difficulty:** Hard
**Link:** https://leetcode.com/problems/alien-dictionary/

## The problem in plain words

Some alien language uses the same letters as us but in a **different alphabetical
order**. You are handed a list of their words that are already sorted by *their*
rules. Work out an order of the letters that fits that sorting. If no order can
explain the list, return `""`.

```diagram
   words (sorted by alien rules):
        wrt
        wrf
        er
        ett
        rftt

   each adjacent pair leaks ONE fact about letter order (below)
```

## Why this matters

You cannot learn much from a single word. The information hides *between* adjacent
words: since the list is sorted, word `i` comes before word `i+1`, and a dictionary
sort compares them letter by letter until the first difference. That first
differing letter is the whole story.

The reusable idea is **recovering one global order from many little pairwise hints**
— and noticing when the hints contradict. Turn each "X before Y" fact into an
arrow, then topologically sort (put every letter in an order where all arrows point
forward). Dependency resolvers infer an install order from many "A before B" rules
and report a conflict when they form a loop. Ranking systems build a standings
order from head-to-head results. Build systems derive compile order from per-file
import edges.

What you are solving for is a consistent order **plus** a clean "impossible" signal.

## Start from the obvious

Compare each adjacent pair and read off its first difference:

```diagram
   "wrt" vs "wrf"  ->  match w,r then differ:  t before f
   "wrf" vs "er"   ->  differ at position 0:   w before e
   "er"  vs "ett"  ->  match e then differ:    r before t
   "ett" vs "rftt" ->  differ at position 0:   e before r

   facts:  t->f   w->e   r->t   e->r
```

Each adjacent pair gives **one** fact: "letter X comes before letter Y." The
matching letters before the difference tell you nothing; the letters after it don't
matter for this pair.

## The insight

Those "X before Y" facts are arrows in a graph over the letters. A valid alien
alphabet is any **topological sort** of that graph — an order where every arrow
points forward. So:

1. **Seed** the graph with every letter that appears (even a letter with no rules
   still belongs in the answer).
2. For each adjacent word pair, find the first differing letter and add arrow
   `a -> b`.
3. **Sort by peeling**: repeatedly emit a letter with nothing pointing at it.

```diagram
   arrows:  w->e   e->r   r->t   t->f

   in-count:  w:0  e:1  r:1  t:1  f:1
   ready (in-count 0): [w]

   emit w -> drop e   e:0   ready:[e]     order: w
   emit e -> drop r   r:0   ready:[r]     order: w e
   emit r -> drop t   t:0   ready:[t]     order: w e r
   emit t -> drop f   f:0   ready:[f]     order: w e r t
   emit f                                 order: w e r t f

   placed all 5 letters  ->  answer "wertf"
```

If the sort can't place every letter, there is a **loop** — the rules contradict
each other (like `x < z` and `z < x`) — so return `""`.

## Find the trap (the prefix rule)

There is one inconsistency the letter comparison misses. If an earlier word is a
**prefix** of a later word, that is fine (`"ab"` before `"abc"`). But the reverse —
a longer word before its own prefix — is **impossible** in any order, because a
prefix always sorts first.

```diagram
   "abc" then "ab"   ->   they match all the way through "ab",
                          but the LONGER one came first.

   no alphabet can make "abc" sort before "ab"   ->  return ""
```

So when two adjacent words match up to the shorter one's length and the earlier
word is longer, return `""` right away. Forgetting this is the classic wrong answer
here.

## Complexity

- **Time: about C steps**, where `C` is the total number of characters across all
  words. Each character is looked at a constant number of times to build arrows, and
  the peel-off sort is linear in letters plus arrows.
- **Extra memory: small and fixed** — at most 26 letters and their arrows.

## Pitfalls

- **The prefix trap** above — the most-missed case.
- **Only the first difference counts.** After the first differing position, stop;
  later letters carry no ordering info for that pair.
- **Seed all letters.** A letter that appears in no rule still belongs in the
  output; start the graph from *every* character first.
- **Loop = invalid.** If the sort emits fewer than all the letters, return `""`.
- **Duplicate arrows.** Adding the same `a -> b` twice would inflate the in-count
  and break the sort — guard with a set before counting it.

## Transfer

"Turn ordering hints into arrows, then peel-sort" is the reusable engine, shared
with [Course Schedule / 207](../0207-course-schedule/) and
[Course Schedule II / 210](https://leetcode.com/problems/course-schedule-ii/)
(finish order),
[Sequence Reconstruction / 444](https://leetcode.com/problems/sequence-reconstruction/),
and any "recover a global order from local comparisons" task.

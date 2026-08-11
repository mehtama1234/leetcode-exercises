# 287. Find the Duplicate Number

**Pattern:** Index-as-hash → linked-list cycle (Floyd's tortoise and hare)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/find-the-duplicate-number/

## The problem in plain words

You have a list of length `n+1` where every value is between 1 and `n`. With `n+1`
values crammed into `n` possible slots, at least one value has to repeat — and here
exactly one value does, possibly many times. Find that repeated value. Two hard rules:
**don't modify the array**, and use only a constant amount of extra memory.

```diagram
   nums = [1, 3, 4, 2, 2]      length 5, values in 1..4

   value counts:  1:once  2:twice  3:once  4:once
   answer = 2
```

## Why this matters

The interesting part isn't finding a duplicate — it's finding one under a resource
lockdown that kills the obvious tools. You can't sort (that modifies the array), you
can't build a set (that's extra memory that grows with the input), and you can't
sign-flip like #442/#448 (that mutates). The way out is a change of *representation*:
read the array as a set of pointers, and the duplicate becomes the entrance of a loop in
an implicit linked list, which two walking pointers can locate with nothing else.

That reframing — "treat `i -> nums[i]` as pointers and reason about loops" — is a
genuinely reusable tool. Detecting a loop in a structure you can't fully store, finding
where a pseudo-random sequence starts repeating (Pollard's rho for integer
factorization is exactly this idea applied to a numeric map), and spotting reference
cycles all lean on it. The constraint "you may not touch the input and you have no room
to spare" is common when the array is shared, memory-mapped, or enormous.

What the good solution buys: constant extra memory on read-only input — no scratch copy,
no set, respecting a hard memory and immutability budget that the easy solutions blow
through.

## Start from the obvious

The bounded range invites the #442-style sign trick — mark value `v`'s home negative;
the first home already negative is the duplicate.

```diagram
   for x in nums:  home = abs(x) - 1
                   if nums[home] < 0: return abs(x)
                   else flip nums[home] negative
```

Constant extra memory, one pass... except it **modifies the array**, which #287 forbids.
(Sorting and a set are the other honest first thoughts, and they fail the same
constraints — one mutates, the other's memory grows with the input.) The real challenge
is doing it read-only.

## Find the waste

Every read-only approach that scans-and-searches (for each value, hunt for a later copy)
re-walks the tail over and over — about `n × n` work. The way to beat that isn't a
cleverer search; it's to stop searching and *change how we read the array*.

Here's the key observation. Build a chain of positions: start at 0, and from position `i`
jump to position `nums[i]`. Because values are in `1..n` and there are `n+1` of them, two
different positions must hold the same value — meaning two positions jump to the **same**
next position. That shared target is a spot with two arrows pointing into it. A walk that
keeps jumping can never fall off the end (values are always valid indices ≥ 1), so it
must eventually revisit a spot: the chain has a **loop**, and the spot where two arrows
converge is the loop's entrance — which is exactly the duplicated value.

```diagram
   nums = [1, 3, 4, 2, 2]     read as "index i points to index nums[i]"

   0 -> 1 -> 3 -> 2 -> 4 -+
             ^            |
             +------------+     both index 3 and index 4 point to index 2

   the loop entrance is index 2, and 2 is the duplicated value
```

## The insight

**Read `i -> nums[i]` as a linked list; the duplicate is the loop's entrance; find it
with Floyd's tortoise and hare.**

Phase 1 — detect the loop and get a meeting point. Move `slow` one hop
(`slow = nums[slow]`) and `fast` two hops (`fast = nums[nums[fast]]`) each step. Inside a
loop the fast pointer laps the slow one, so they collide somewhere in the loop.

Phase 2 — locate the entrance. Reset `slow` to the start (`nums[0]`), keep `fast` at the
meeting point, and now move **both one hop at a time**. Floyd's distance math guarantees
they meet exactly at the loop's entrance.

```diagram
   chain:  0 -> 1 -> 3 -> 2 -> 4 -> 2 -> 4 -> ...   (loop is 2 -> 4 -> 2)

   phase 1 (slow +1, fast +2), starting both at nums[0]=1:
     step  slow      fast
      1    nums[1]=3 nums[nums[1]]=nums[3]... = 2
      2    2         2      <- collide at value 2 (inside the loop)

   phase 2: slow back to start (nums[0]=1), fast stays at 2, both +1:
     slow: 1 -> 3 -> 2
     fast: 2 -> 4 -> 2
                    ^ meet at 2 = the loop entrance = the duplicate
```

Why phase 2 works: if the distance from the start to the entrance is `a`, and the meeting
point is `b` steps into a loop of length `c`, the fast pointer's double speed forces
`a` and `c - b` to line up (they're equal, counting around the loop). So walking `a` steps
from the start and `a` steps from the meeting point both land on the entrance. Nothing is
written; two integer pointers are the entire memory cost.

## Complexity

- **Time:** about `n` steps — each phase is a linear number of hops; the pointers travel
  a bounded multiple of the loop and tail length.
- **Extra memory:** constant — two index variables, and the array is never modified.

## Pitfalls

- **Seeding the walk.** The traversal is over *values as next-pointers*; seed both
  pointers with `nums[0]`. The algorithm relies on 0 never being a value (guaranteed,
  since values are ≥ 1), so index 0 is a safe start outside the loop.
- **Fusing the two phases.** Phase 1 finds a meeting point *inside* the loop, not the
  entrance. You must run phase 2 (equal speed from the start) to get the answer.
- **Reaching for the sign-flip trick.** Constant memory, yes, but it mutates the input —
  disqualified here.
- **Assuming exactly one duplicated *slot*.** The value may repeat many times; the loop
  argument still pins down the single repeated *value*.

## Transfer

Two transferable ideas live here. First, *index-as-hash* ties it to its chapter siblings
[Find All Duplicates / 442](../0442-find-all-duplicates-in-an-array/) and
[Find All Numbers Disappeared / 448](../0448-find-all-numbers-disappeared-in-an-array/)
— but the read-only rule blocks their sign trick. Second, *Floyd's cycle detection*,
which powers [Linked List Cycle / 141](../../05-linked-list/0141-linked-list-cycle/) and
[Linked List Cycle II / 142](../../05-linked-list/0142-linked-list-cycle-ii/): whenever
"for each x, jump to f(x)" over a finite set must eventually repeat, two pointers at 1×
and 2× speed find where the repetition begins in constant space.

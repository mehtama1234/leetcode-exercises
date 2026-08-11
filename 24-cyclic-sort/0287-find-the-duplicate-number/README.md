# 287. Find the Duplicate Number

**Pattern:** Index-as-hash → linked-list cycle (Floyd's tortoise and hare)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/find-the-duplicate-number/

## The problem in plain words

You have a list of length n+1 where every value is between 1 and n. By the
pigeonhole principle at least one value repeats — and here exactly one value does,
possibly many times. Find that repeated value. Two hard rules: **don't modify the
array**, and use only **O(1) extra space**.

## Why this matters

The interesting part isn't finding a duplicate — it's finding one under a resource
lockdown that kills the obvious tools. You can't sort (that modifies the array),
you can't hash (that's O(n) space), and you can't sign-flip like #442/#448 (that
mutates). The way out is a change of *representation*: read the array as a function
and the duplicate becomes the entrance of a cycle in an implicit linked list, which
Floyd's algorithm locates with two pointers and nothing else.

That reframing — "treat `i → nums[i]` as pointers and reason about cycles" — is a
genuinely reusable tool. Detecting a loop in a linked structure or a state machine
you can't fully store, finding where a pseudo-random generator's sequence starts
repeating (Pollard's rho for integer factorization is Floyd's cycle-finding
applied to a numeric map), and spotting reference cycles all lean on the same
two-pointer trick. The constraint "you may not touch the input and you have no room
to spare" is common when the array is memory-mapped, shared, or enormous.

What the good solution buys is O(1) space on read-only input: it answers the
question without a scratch copy or a hash set, respecting a hard memory and
immutability budget that the easy solutions blow through.

## Start from the obvious

The bounded range invites the #442-style sign trick — mark value `v`'s home
negative; the first home already negative is the duplicate:

```
for x in nums:
    home = abs(x) - 1
    if nums[home] < 0: return abs(x)
    nums[home] = -nums[home]
```

It's O(n)/O(1)... except it **modifies the array**, which #287 forbids. (Sorting
and a hash set are the other honest first thoughts, and they fail the same
constraints — one mutates, the other costs O(n) space.) The real challenge is
doing it read-only.

## Find the waste

Every read-only approach that scans-and-searches (for each value, look for a later
copy) is O(n²) — it re-scans the tail over and over. The way to beat that isn't a
cleverer search; it's to stop searching and *change how we read the array*.

Here's the key observation. Build a sequence of positions: start at 0, and from
position `i` jump to position `nums[i]`. Because values are in 1..n and there are
n+1 of them, two different positions must hold the same value — meaning two
positions jump to the **same** next position. That shared target is a node with
two incoming arrows. A walk that keeps jumping can never fall off the end (values
are always valid indices ≥ 1), so it must eventually revisit a node: the sequence
has a **cycle**, and the node where two arrows converge is the cycle's entrance —
which is precisely the duplicated value.

## The insight

**Read `i → nums[i]` as a linked list; the duplicate is the cycle's entrance; find
it with Floyd's tortoise and hare.**

Phase 1 — detect the cycle and get a meeting point. Move `slow` one hop
(`slow = nums[slow]`) and `fast` two hops (`fast = nums[nums[fast]]`) per step.
Inside a cycle the fast pointer laps the slow one, so they collide somewhere in the
loop.

Phase 2 — locate the entrance. Reset `slow` to the start (`nums[0]`), keep `fast`
at the meeting point, and now advance **both one hop at a time**. Floyd's distance
identity guarantees they meet exactly at the cycle's entrance:

```
slow = fast = nums[0]
while True:
    slow = nums[slow]; fast = nums[nums[fast]]
    if slow == fast: break
slow = nums[0]
while slow != fast:
    slow = nums[slow]; fast = nums[fast]
return slow
```

Why phase 2 works: if the distance from the start to the entrance is `a` and the
meeting point is `b` steps into the cycle of length `c`, the fast pointer's
double speed forces `a ≡ (c − b) (mod c)`. So walking `a` steps from the start and
`a` steps from the meeting point both land on the entrance. Nothing is written; two
integer pointers are the entire memory cost.

## Complexity

- **Time:** `O(n)` — each phase is a linear number of hops; the pointers travel a
  bounded multiple of the cycle/tail length.
- **Space:** `O(1)` — two index variables, and the array is never modified.

## Pitfalls

- **Starting the two-pointer walk from index 0 as a value.** The traversal is over
  *values as next-pointers*; seed both pointers with `nums[0]`, and the algorithm
  relies on 0 never being a value (guaranteed, since values are ≥ 1) so index 0 is
  a safe, outside-the-cycle start.
- **Fusing the two phases.** Phase 1 finds a meeting point *inside* the cycle, not
  the entrance. You must run phase 2 (equal speed from the start) to get the answer.
- **Reaching for the sign-flip trick.** It's O(n)/O(1) but mutates the input —
  disqualified here.
- **Assuming exactly one duplicated *slot*.** The value may repeat many times; the
  cycle argument still pins down the single repeated *value*.

## Transfer

Two transferable ideas live here. First, *index-as-hash* ties it to its chapter
siblings [Find All Duplicates / 442](../0442-find-all-duplicates-in-an-array/) and
[Find All Numbers Disappeared / 448](../0448-find-all-numbers-disappeared-in-an-array/)
— but the read-only rule blocks their sign trick. Second, *Floyd's cycle
detection*, which powers
[Linked List Cycle / 141](../../05-linked-list/0141-linked-list-cycle/) and
[Linked List Cycle II / 142](../../05-linked-list/0142-linked-list-cycle-ii/):
whenever "for each x, jump to f(x)" over a finite set must eventually repeat, two
pointers at 1× and 2× speed find where the repetition begins in O(1) space.

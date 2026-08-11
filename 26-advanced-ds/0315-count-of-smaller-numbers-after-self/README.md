# 315. Count of Smaller Numbers After Self

**Pattern:** Fenwick tree as a running frequency counter over value-ranks
**Difficulty:** Hard
**Link:** https://leetcode.com/problems/count-of-smaller-numbers-after-self/

## The problem in plain words

For each element, count how many elements to its *right* are strictly smaller than
it. Return that list of counts, one per position.

```diagram
   nums  = [ 5, 2, 6, 1 ]

   5 -> to its right: 2,6,1 ; smaller than 5: {2,1}    -> 2
   2 -> to its right: 6,1   ; smaller than 2: {1}      -> 1
   6 -> to its right: 1     ; smaller than 6: {1}      -> 1
   1 -> to its right: (none)                           -> 0

   answer = [2, 1, 1, 0]
```

## Why this matters

The plain definition is "for each element, scan its whole right side." That
re-scans the same suffix again and again. The real question underneath is: *as I
move leftward through the array, how many of the values I've already passed are
smaller than the one I'm on now?* If you could answer "how many seen-so-far values
are below `v`" in one cheap step, the whole thing collapses to one pass.

Counting how many earlier items fall below a threshold is the shape of many
problems: how many trades cleared under a price, how many events landed before a
cutoff, how many inversions a list has (a measure of how unsorted it is). A Fenwick
tree used as a live tally answers "how many values so far are <= v" in about
`log n`, which is what makes the one-pass solution possible.

## Start from the obvious

For each element, walk everything to its right and tally the strictly smaller ones.

```diagram
   [5, 2, 6, 1]

   i=0 (5): scan 2,6,1  -> 2 smaller
   i=1 (2): scan 6,1    -> 1 smaller
   i=2 (6): scan 1      -> 1 smaller
   i=3 (1): scan (none) -> 0
            ^ each i re-walks its entire suffix
```

Correct and obvious — and about `n x n` steps, because every element re-scans the
tail to its right. That repeated scanning is the waste.

## The insight

Process the array from **right to left**, and keep a running tally of the values
you've inserted so far in a Fenwick tree. When you reach `nums[i]`, everything
already in the tree lies to its right — so "how many smaller values are to my
right?" becomes "how many already-inserted values are strictly less than
`nums[i]`?" That's a prefix-count query.

Values can be huge or negative, so first squash them to small ranks: sort the
distinct values and map each to its position (1, 2, 3, ...). Now the tree is
indexed by rank, and each slot counts how many times a rank has been inserted.

```diagram
   nums = [5, 2, 6, 1]
   sorted distinct = [1, 2, 5, 6]
   ranks:  1->1   2->2   5->3   6->4

   Fenwick counts inserted ranks; query prefix(rank-1) = how many smaller so far.
   Walk RIGHT to LEFT:

   i=3, val=1 (rank 1): prefix(0) = 0        result[3]=0 ; insert rank 1
   i=2, val=6 (rank 4): prefix(3) = 1        result[2]=1 ; insert rank 4
   i=1, val=2 (rank 2): prefix(1) = 1        result[1]=1 ; insert rank 2
   i=0, val=5 (rank 3): prefix(2) = 2        result[0]=2 ; insert rank 3

   answer = [2, 1, 1, 0]
```

The Fenwick tree makes both the insert and the prefix-count run in about `log n`
by walking the lowest-set-bit chain. Each rank sits in a chain of power-of-two
blocks; inserting climbs the blocks that cover it, counting peels blocks off to
sum ranks `1..r`.

```diagram
   Fenwick over ranks 1..4, after inserting ranks {1, 4}:

   tree buckets (each covers a block ending at its index):
     node 1 (001): counts rank {1}          -> 1
     node 2 (010): counts ranks {1,2}       -> 1
     node 3 (011): counts rank {3}          -> 0
     node 4 (100): counts ranks {1,2,3,4}   -> 2

   prefix(2) = "how many inserted with rank <= 2"
     i=2 (010): add tree[2]=1   strip low bit -> 0   -> total 1
```

The kept merge-sort version is the other classic answer: sort indices by value and,
during each merge, count how many right-half elements slip in front of a left-half
element — those are exactly the smaller-and-to-the-right ones.

## Complexity

- **Time: about n log n.** One pass right-to-left; each step does a `log n` insert
  and a `log n` prefix-count in the Fenwick tree. Compression is a one-time sort.
- **Extra memory: about n.** The rank map, the result array, and the tree.

## Pitfalls

- Querying `prefix(rank)` instead of `prefix(rank - 1)` — you want *strictly*
  smaller, so exclude the current value's own rank.
- Forgetting to coordinate-compress: raw values can be enormous or negative, which
  would blow up the tree size.
- Walking left-to-right by mistake. The right-to-left order is what makes
  "already inserted" mean "to my right."

## Transfer

The reusable move is **use a Fenwick tree as a live frequency counter, so
"how many values seen so far are below v" is a log-n prefix query.** It shares its
machinery with [Range Sum Query - Mutable / 307](../0307-range-sum-query-mutable/),
and the counting-during-merge alternative is the same inversion count behind
[Reverse Pairs / 493](https://leetcode.com/problems/reverse-pairs/).

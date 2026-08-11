# 307. Range Sum Query - Mutable

**Pattern:** Fenwick tree (Binary Indexed Tree) — store partial sums, not raw values
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/range-sum-query-mutable/

## The problem in plain words

You have an array. Two operations arrive in any order, over and over:
`update(i, val)` changes one element, and `sumRange(l, r)` asks for the sum of the
slice from `l` to `r` inclusive. Both have to stay fast even as the array keeps
changing.

```diagram
   nums = [1, 3, 5]

   sumRange(0, 2)  ->  1 + 3 + 5 = 9
   update(1, 2)    ->  nums = [1, 2, 5]
   sumRange(0, 2)  ->  1 + 2 + 5 = 8
```

## Why this matters

The whole problem is a tug-of-war between the two operations. A plain array makes
`update` instant but `sumRange` slow (you add up the whole slice each time). A
prefix-sum array flips it: `sumRange` is instant, but a single `update` forces you
to rewrite every prefix after it. You can make one fast only by making the other
slow — unless you store something cleverer than either.

That tension — fast reads *and* fast writes over a range — is everywhere: a
running leaderboard where scores change and you query totals, a spreadsheet
recomputing column sums as cells edit, a database index over a mutable column. The
Fenwick tree is the compact answer: store *partial* sums arranged so both
operations touch only about `log n` of them.

## Start from the obvious

A prefix-sum array. `prefix[k]` holds the sum of the first `k` elements, so any
range sum is one subtraction.

```diagram
   nums   =  [1,  3,  5]
   prefix = [0, 1,  4,  9]     prefix[k] = sum of first k

   sumRange(0,2) = prefix[3] - prefix[0] = 9 - 0 = 9   (instant)

   now update(1, 2):  nums -> [1, 2, 5]
   prefix[2], prefix[3] are BOTH wrong now, must be rewritten
   prefix = [0, 1, 3, 8]
            ^^^^^^^^^^^ every prefix at/after the change shifts
```

Range queries are instant, but every update rewrites the whole tail — slow once
updates are frequent. The waste: one small change forces a full rebuild of half
the prefix array.

## The insight

Store *partial* sums, each covering a block of the array whose length is a power
of two. The tree is 1-indexed, and node `i` is responsible for the sum of a block
ending at `i` whose length equals `i`'s lowest set bit (`i & -i`).

```diagram
   values (1-indexed):  a1  a2  a3  a4  a5  a6  a7  a8

   which block does each Fenwick node cover?  (length = lowest set bit)

   node 1 (0001): [a1]                 len 1
   node 2 (0010): [a1 a2]              len 2
   node 3 (0011): [a3]                 len 1
   node 4 (0100): [a1 a2 a3 a4]        len 4
   node 5 (0101): [a5]                 len 1
   node 6 (0110): [a5 a6]              len 2
   node 7 (0111): [a7]                 len 1
   node 8 (1000): [a1 a2 a3 a4 ... a8] len 8
```

Every position is covered by a chain of these blocks whose lengths are distinct
powers of two — exactly the `1` bits of the index. To sum the first `i` elements,
add `tree[i]`, then strip the lowest set bit to jump to the block before it, and
repeat.

```diagram
   prefix sum up to index 7  (7 = 0111):

   i=7 (0111): add tree[7]  = [a7]           strip low bit -> 6
   i=6 (0110): add tree[6]  = [a5 a6]        strip low bit -> 4
   i=4 (0100): add tree[4]  = [a1 a2 a3 a4]  strip low bit -> 0
   i=0: stop

   total = a1+a2+a3+a4 + a5+a6 + a7   = sum of first 7
   ^ three blocks, one per 1-bit of 7 -> about log n additions
```

An update walks the *other* way: add the change to `tree[i]`, then move to the
next node that also covers `i` by *adding* the lowest set bit (`i += i & -i`).
Again about `log n` nodes. A range sum is `prefix(r) - prefix(l-1)`.

```diagram
   update(index 5, +delta):  (1-indexed node 5)

   i=5 (0101): tree[5] += delta   add low bit -> 6
   i=6 (0110): tree[6] += delta   add low bit -> 8
   i=8 (1000): tree[8] += delta   add low bit -> past end, stop
              ^ only the nodes whose block covers position 5
```

The kept segment-tree version is the other standard answer: a binary tree of range
sums flattened into an array, also `log n` for both operations and more general
(it works for min, max, gcd — any way of combining two ranges), at the cost of
about twice the memory.

## Complexity

- **Time: about log n per operation.** Both `update` and `sumRange` touch one node
  per set bit of the index — at most the number of bits.
- **Extra memory: about n.** One tree array the size of the input (plus one).
  Building it is `n` point-updates, about `n log n` up front.

## Pitfalls

- Off-by-one from mixing 0-indexed array positions with the 1-indexed tree. The
  `+1` shift into tree space is easy to drop.
- On `update`, applying the raw new value instead of the *difference* from the old
  one — the tree stores sums, so it needs the delta.
- Confusing the two walks: `i -= i & -i` sums a prefix (moving down), `i += i & -i`
  updates (moving up).

## Transfer

The reusable move is **keep partial aggregates in a tree so a point change and a
range query each touch only about log n of them.** The same Fenwick tree, used as
a frequency counter, powers
[Count of Smaller Numbers After Self / 315](../0315-count-of-smaller-numbers-after-self/),
and the segment-tree cousin generalizes to range-min or range-max queries over a
mutable array.

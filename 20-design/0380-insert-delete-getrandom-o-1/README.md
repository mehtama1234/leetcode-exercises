# 380. Insert Delete GetRandom O(1)

**Pattern:** Hash map + array (swap-with-last for O(1) delete)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/insert-delete-getrandom-o-1/

## The problem in plain words

Build a set of integers with three operations, each averaging a fixed cost:
`insert(val)` adds if absent, `remove(val)` drops if present, and `getRandom()`
returns one current element with every element equally likely. `insert` and
`remove` also report whether they actually changed the set.

```diagram
   insert(1) -> {1}        insert(2) -> {1,2}
   remove(1) -> {2}        getRandom() -> pick uniformly from {2}
```

## Why this matters

The lesson is that **no single structure gives you everything**, so you combine two
whose strengths cover each other's weak spots. A hash set nails membership,
insert, and delete in fixed time — but has no notion of "the i-th element," so you
can't pick a uniform random one without walking it. An array nails random indexing
in fixed time — but deleting a middle element is slow because everything after it
shifts. Put them together and all three operations become fixed-cost.

Drawing a uniform random member from a live, changing set is a real need. Load
balancers and schedulers pick a random healthy backend. A/B testing and
reservoir-style sampling draw random members from a shifting population. Randomized
algorithms with random pivots, fair matchmaking, and random-policy cache eviction
all want "give me a random current element, fast."

What the good solution buys is keeping **all three operations fixed-cost** as the
set grows — no operation quietly degrades to a full scan, which is what a latency
budget demands when the set is hot.

## Start from the obvious

Use a hash set. Insert and remove are fixed-cost. But `getRandom`?

```diagram
   set = { 4, 9, 2, 7 }   (no positions inside a hash set)

   getRandom must copy it out to a list first:
       list(set) = [4, 9, 2, 7]  ->  pick an index
       ^ that copy is a full pass, every call
```

A hash set has no positional index, so to pick uniformly you convert it to a list
first — a full pass every call. The other option, a plain array, makes `getRandom`
easy but `remove(val)` must find `val` and then shift everything after it. Either
way one operation is slow.

## Find the waste

The array's remove is slow only because it insists on keeping order — it shifts to
close the gap. But this is a **set**: order carries no meaning. If order doesn't
matter, don't preserve it. You can fill the hole with *any* element, and the
cheapest one to grab is the last.

## The insight

Keep both structures in sync:

- `vals` — an array of the current elements, in whatever order.
- `pos` — a dict mapping `value -> its index in vals`.

```diagram
   vals = [ 10, 20, 30, 40 ]        pos = { 10:0, 20:1, 30:2, 40:3 }
                    ^
   remove(20): idx = pos[20] = 1

   1) copy the LAST element (40) into the hole at index 1:
        vals = [ 10, 40, 30, 40 ]   pos[40] = 1   (40's index updated)
   2) pop the now-duplicated last slot, drop 20 from pos:
        vals = [ 10, 40, 30 ]       pos = { 10:0, 40:1, 30:2 }
                                          ^ no shifting -- fixed cost
```

Now each operation is fixed-cost:

- **insert:** append to `vals`, record its index in `pos`.
- **remove:** look up the index in `pos`, copy the last element into that slot, fix
  the moved element's index in `pos`, then pop the last slot and delete the value.
- **getRandom:** a random index into `vals` — uniform and one step.

The swap-with-last trick is the whole game: it turns a slow middle deletion into a
fast end deletion, because a set lets you reorder freely.

## Complexity

- **Time: fixed cost on average** for insert, remove, and getRandom. Hash
  operations are fixed on average; array append, pop-from-end, and indexing are all
  one step.
- **Space: about n.** The array and the dict each hold one entry per element.

## Pitfalls

- Forgetting to update `pos` for the element you moved from the end into the hole.
  Its index changed; skip this and the dict lies.
- Removing the element that *is* the last one. The swap becomes a no-op — make sure
  the code still pops and deletes correctly (it does, since it swaps with itself).
- Returning values or booleans inconsistently — `insert`/`remove` must report
  whether they changed the set.
- Trying to keep `vals` sorted or ordered. It must be free-form for a fast delete.

## Transfer

The "hash map for lookup + array for indexing, swap-with-last to delete" combo
reappears in
[Insert Delete GetRandom O(1) - Duplicates allowed / 381](https://leetcode.com/problems/insert-delete-getrandom-o1-duplicates-allowed/)
(store a set of indices per value). The broader "pair two structures so each covers
the other's weak operation" idea also drives
[LRU Cache / 146](../0146-lru-cache/) and
[LFU Cache / 460](../0460-lfu-cache/).

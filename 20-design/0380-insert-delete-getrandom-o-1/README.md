# 380. Insert Delete GetRandom O(1)

**Pattern:** Hash map + array (swap-with-last for O(1) delete)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/insert-delete-getrandom-o-1/

## The problem in plain words

Build a set of integers with three operations, each averaging O(1):
`insert(val)` (add if absent), `remove(val)` (drop if present), and
`getRandom()` (return one current element, each equally likely). `insert` and
`remove` return whether they actually changed the set.

## Why this matters

The lesson is that **no single structure gives you everything**, so you combine
two whose strengths cover each other's weaknesses. A hash set nails O(1)
membership, insert, and delete — but has no notion of "the i-th element," so you
can't pick a uniform random one without walking it. An array nails O(1) random
indexing — but deleting a middle element is O(n) because everything shifts. Put
them together and all three operations are O(1).

Uniform random sampling from a live, changing set is a real need. Load balancers
and schedulers pick a random healthy backend. A/B testing and reservoir-style
sampling draw random members from a mutating population. Randomized algorithms
(random pivots, Monte Carlo methods), fair matchmaking, and cache eviction with a
random policy all want "give me a random current element, fast."

What the good solution buys is keeping **all three operations O(1)** as the set
grows — no operation degrades to a scan, which is what a latency budget demands
when the set is hot.

## Start from the obvious

Use a hash set. Insert and remove are O(1). But `getRandom`?

```
def getRandom(self):
    return random.choice(list(self.s))   # O(n): materializes the whole set
```

A hash set has no positional index, so to pick uniformly you convert it to a list
first — O(n) every call. Alternatively, use a plain array: `getRandom` is easy,
but `remove(val)` must find `val` (O(n)) and shift everything after it (O(n)).
Either way one operation is O(n).

## Find the waste

The array's remove is slow only because it insists on keeping order — it shifts
to close the gap. But this is a **set**: order doesn't matter. If order is
irrelevant, we don't have to preserve it. We can fill the hole with *any*
element, and the cheapest one to grab is the last.

## The insight

Keep both structures, synchronized:

- `vals` — an array of the current elements, in arbitrary order.
- `pos` — a dict mapping `value -> its index in vals`.

Now each operation is O(1):

- **insert:** append to `vals`, record its index in `pos`.
- **remove:** look up the value's index in `pos`. Copy the *last* element of
  `vals` into that slot, fix that moved element's index in `pos`, then `pop` the
  last slot and delete the value from `pos`. Removing from the end is O(1), so no
  shifting.
- **getRandom:** a random index into `vals` — uniform and O(1).

The swap-with-last trick is the whole game: it turns an O(n) middle deletion into
an O(1) end deletion, because a set lets us reorder freely.

## Complexity

- **Time:** `O(1)` average for insert, remove, and getRandom (hash operations are
  O(1) average; array append/pop-from-end and index are O(1)).
- **Space:** `O(n)` — the array and the dict each hold one entry per element.

## Pitfalls

- Forgetting to update `pos` for the element you moved from the end into the
  hole. Its index changed; skip this and the dict lies.
- Removing the element that *is* the last one. The swap becomes a no-op — make
  sure the code still pops and deletes correctly (it does, since it swaps with
  itself).
- Returning values or booleans inconsistently — `insert`/`remove` must report
  whether they changed the set.
- Trying to keep `vals` sorted or ordered. It must be free-form for O(1) delete.

## Transfer

The "hash map for lookup + array for indexing, swap-with-last to delete" combo
reappears in
[Insert Delete GetRandom O(1) - Duplicates allowed / 381](https://leetcode.com/problems/insert-delete-getrandom-o1-duplicates-allowed/)
(store a set of indices per value). The broader "pair two structures so each
covers the other's weak operation" idea also drives
[LRU Cache / 146](../0146-lru-cache/) and
[LFU Cache / 460](../0460-lfu-cache/).

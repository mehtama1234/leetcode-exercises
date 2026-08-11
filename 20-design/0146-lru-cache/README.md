# 146. LRU Cache

**Pattern:** Hash map + doubly linked list (O(1) ordered cache)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/lru-cache/

## The problem in plain words

Build a small cache that holds at most `capacity` key/value pairs. `get(key)`
returns the value (or -1 if absent). `put(key, value)` stores a pair. When the
cache is already full and a brand-new key arrives, throw out the entry that was
used longest ago — the "least recently used" one. Both operations must be O(1).

## Why this matters

Underneath this is one operation: *keep the hottest items reachable and cheaply
forget the cold ones, all in constant time.* Memory is finite, so a cache must
decide what to drop, and "the thing nobody has touched in a while" is a good
guess at what won't be needed soon.

This is not a toy. Operating systems evict memory pages with LRU-style policies.
CPU caches, database buffer pools (Postgres, MySQL), and CDN edge nodes all keep
recently touched blocks and drop stale ones. Redis and Memcached ship LRU
eviction as a headline feature. Your browser's back/forward cache and image
caches lean on the same idea.

What the good solution buys is a **latency budget**: every access stays O(1) no
matter how large the cache grows. A naive "scan to find the oldest" cache turns
each eviction into an O(n) sweep — fine for 10 items, fatal for a hot cache
serving millions of requests a second.

## Start from the obvious

Store the pairs in a dict for fast lookup, and keep a separate list of keys in
use-order to know who is oldest.

```
map[key] = value
order = [key, ...]        # oldest at front, newest at end
# on access: order.remove(key); order.append(key)
# on evict:  victim = order.pop(0); del map[victim]
```

Lookups are O(1), but `order.remove(key)` and `pop(0)` on a Python list are
O(n) — they shift elements. So `get` and `put` degrade to O(n). Correct, but it
misses the required complexity.

## Find the waste

The waste is *searching a list to move or delete one element*. In an array you
must shift everything after the hole. But if each item knew its own neighbours,
you could splice it out in O(1) — no scan, no shift.

That is exactly a **doubly linked list**: each node has a `prev` and `next`, so
removing it is just rewiring two pointers. And to jump straight to a node
without walking the list, keep a **dict from key -> node**.

## The insight

Run two structures together:

1. A **doubly linked list** ordered by recency. Most-recently-used sits at the
   front, least-recently-used at the back.
2. A **dict** mapping key -> the node holding it.

- `get`: dict finds the node (O(1)); unlink it and re-insert at the front.
- `put` (existing key): update value, move node to front.
- `put` (new key, full): the node just before the back sentinel is the LRU —
  unlink it and delete it from the dict, then insert the new node at the front.

Use two sentinel nodes (`head`, `tail`) so there is always a real node on either
side of any position. That erases every "am I at the end?" special case.

## Complexity

- **Time:** `O(1)` for both `get` and `put` — the dict does the finding, the
  linked list does the reordering, and neither ever scans.
- **Space:** `O(capacity)` — one node and one dict entry per stored key.

## Pitfalls

- Forgetting to update recency on `get`. A read *is* a use.
- Updating an existing key's value but not moving it to the front — it can then
  be wrongly evicted.
- Off-by-one at the list ends. Sentinels remove these; without them you must
  null-check `prev`/`next` everywhere.
- Deleting from the dict but not unlinking the node (or vice versa) — the two
  structures must stay in sync.

## Transfer

The move "pair a hash map with a linked list so you get O(1) lookup *and* O(1)
ordered removal" is the core of most cache designs. See
[LFU Cache / 460](../0460-lfu-cache/), which adds frequency on top of recency,
and [All O`one Data Structure / 432](https://leetcode.com/problems/all-oone-data-structure/).
Any time you need "fast lookup plus fast reorder/evict," reach for this pair.

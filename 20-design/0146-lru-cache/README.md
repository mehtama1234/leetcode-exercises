# 146. LRU Cache

**Pattern:** Hash map + doubly linked list (O(1) ordered cache)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/lru-cache/

## The problem in plain words

Build a small box that holds at most `capacity` key/value pairs. `get(key)` hands
back the value, or -1 if it isn't there. `put(key, value)` stores a pair. When the
box is full and a brand-new key shows up, throw out whatever was touched longest
ago — the "least recently used" entry — to make room. Every `get` and `put` must
take the same tiny amount of time no matter how big the box gets.

```diagram
   capacity = 2         box (most-recent on the left)

   put(1,A)    ->   [ 1:A ]
   put(2,B)    ->   [ 2:B | 1:A ]          full
   get(1)      ->   [ 1:A | 2:B ]          reading 1 makes it most-recent
   put(3,C)    ->   [ 3:C | 1:A ]          full again -> evict 2 (oldest)
                             ^ key 2 fell off the right end
```

## Why this matters

One question sits under all of it: *keep the hot items reachable and cheaply
forget the cold ones, every single time, in constant work.* Memory runs out, so a
cache must pick something to drop, and "the thing nobody has touched in a while"
is a fair guess at what won't be wanted soon.

This runs real machines. Operating systems drop memory pages this way. CPU caches,
database buffer pools in Postgres and MySQL, and CDN edge servers all hold the
recently touched blocks and shed the stale ones. Redis and Memcached ship this
eviction as a headline feature. Your browser's back/forward cache leans on it too.

What the good version buys you is a promise: every access stays fast no matter how
large the cache grows. A lazy "scan the whole thing to find the oldest" cache
turns each eviction into a full sweep — fine for 10 items, deadly for a hot cache
answering millions of requests a second.

## Start from the obvious

Store the pairs in a dict for fast lookup. Keep a separate list of keys in
use-order so you know who is oldest.

```diagram
   map  = { 1:A, 2:B, 3:C }
   order = [ 1, 2, 3 ]        oldest on the left, newest on the right

   touch key 1:  remove it from the middle, put it on the right
   order = [ 2, 3 ] -> [ 2, 3, 1 ]
                   ^ everything after the hole slides left to close it
```

Lookups are fast, but that "remove from the middle" step on a plain list has to
shift every element after the hole. On a list of length n that is about n steps.
So `get` and `put` quietly become slow. Correct, but it misses the required speed.

## Find the waste

The waste is *searching a list to move or delete one item*. In an array you must
shift everything past the gap. But if each item knew its own two neighbours, you
could snip it out by rewiring a couple of pointers — no scan, no shift.

That is a **doubly linked list**: each node holds a `prev` and a `next`, so pulling
it out is two pointer changes. And to reach a node instantly without walking the
chain, keep a **dict from key -> that node**. The dict finds; the list reorders.

## The insight

Run the two structures together:

1. A **doubly linked list** ordered by recency — most-recently-used at the front,
   least-recently-used at the back.
2. A **dict** mapping each key to the node that holds it.

Use two dummy end-caps (`head` and `tail`) that never carry data, so there is
always a real node on either side of any spot you touch — no "am I at the end?"
special cases.

```diagram
   head <-> [1:A] <-> [2:B] <-> tail        (front .... back)

   get(1):  dict jumps straight to node 1, then we splice it to the front.

   1) unlink node 1:
        head <-> [2:B] <-> tail
                            (1 is floating, holding a value)

   2) re-insert at front:
        head <-> [1:A] <-> [2:B] <-> tail
                 ^ now most-recent; 2:B is now the eviction candidate
```

- `get`: dict finds the node, unlink it, re-insert at the front.
- `put` on an existing key: overwrite the value, move the node to the front.
- `put` on a new key when full: the node just before `tail` is the LRU — unlink
  it, delete its key from the dict, then insert the new node at the front.

## Complexity

- **Time: constant per call.** Both `get` and `put` take the same small amount of
  work regardless of size — the dict does the finding, the list does the
  reordering, and neither ever scans.
- **Extra memory: about `capacity`.** One node and one dict entry per stored key.

## Pitfalls

- Forgetting to update recency on `get`. A read *is* a use.
- Overwriting an existing key's value but not moving it to the front — then it can
  be evicted by mistake.
- Off-by-one at the list ends. The dummy end-caps erase these; without them you
  must null-check `prev`/`next` everywhere.
- Deleting from the dict but not unlinking the node, or the reverse — the two
  structures must always agree.

## Transfer

The move "pair a hash map with a linked list so you get fast lookup *and* fast
ordered removal" is the spine of most cache designs. See
[LFU Cache / 460](../0460-lfu-cache/), which stacks frequency on top of recency,
and [All O`one Data Structure / 432](https://leetcode.com/problems/all-oone-data-structure/).
Any time you need "fast lookup plus fast reorder/evict," reach for this pair.

# 460. LFU Cache

**Pattern:** Hash maps + per-frequency ordered buckets (O(1) LFU with LRU tie-break)
**Difficulty:** Hard
**Link:** https://leetcode.com/problems/lfu-cache/

## The problem in plain words

A fixed-size key/value cache. `get` and `put` work as usual, but when the cache is
full and a new key arrives, evict the key that has been used the *fewest* times —
the "least frequently used." If several keys tie for fewest uses, evict the one
among them that was touched longest ago (least recently used). Both operations must
take a fixed amount of time.

```diagram
   capacity = 2

   put(1,A)  put(2,B)   ->   counts: 1->1, 2->1
   get(1)               ->   counts: 1->2, 2->1     (using 1 bumps its count)
   put(3,C)             ->   full; evict the fewest-used = key 2
                            ^ key 1 was used twice, so it survives
```

## Why this matters

LFU asks a subtler question than LRU: not "what's cold *right now*," but "what's
been cold *the whole time*." Tracking how often each item is used, and evicting the
rarest, resists a one-off burst that would wrongly promote an item under pure
recency.

This is a real caching policy. Database buffer pools and storage tiers use LFU, and
LFU/LRU hybrids like ARC and W-TinyLFU (which powers Caffeine, the JVM cache behind
many services) to keep genuinely hot pages. CDNs weigh how *often* an object is
requested, not just how recently. Memory allocators and page-replacement research
lean on frequency counts.

The hard part — and what the good solution buys — is doing all this in **fixed
time**. The obvious frequency cache scans for the smallest count on every eviction,
a full pass. Getting eviction, count bumps, and tie-breaking all down to a fixed
cost is what makes LFU usable in a hot path with a strict latency budget.

## Start from the obvious

Keep a `key -> value` map and a `key -> count` map. On eviction, scan the counts for
the smallest, break ties somehow, and drop that key.

```diagram
   counts = { 1:5, 2:1, 3:9, 4:1 }
              scan all of them to find the min (1)  -> a full pass
              then scan again among the 1s to pick the oldest -> another pass
```

`get`/`put` are fixed-cost, but every eviction scans all keys for the minimum
count, and the tie-break (which of the min-count keys is least recent?) needs even
more bookkeeping. Correct, but it misses the required speed.

## Find the waste

Two things get recomputed. First, the scan for the minimum count on each eviction,
even though that minimum changes in small, predictable steps. Second, nothing
remembers *recency within a count*, so ties force another scan.

Both point to the same fix: **group keys by their count**, and inside each group
keep them in recency order.

## The insight

Maintain three maps plus one integer:

- `key_val`: `key -> value`.
- `key_freq`: `key -> use count`.
- `freq_keys`: `count -> ordered list of keys at that count`, oldest at the front,
  newest at the back.
- `min_freq`: the smallest count any live key currently has.

Use an ordered dict for each bucket: it gives a fast append-to-end (newest) and a
fast pop-from-front (oldest) — a ready-made recency list.

```diagram
   min_freq = 1

   count 1:  [ 2, 4 ]        (oldest .. newest)
   count 2:  [ 1 ]

   touch key 4  (get or update):
     lift 4 out of bucket 1, bump its count to 2, append to bucket 2:
       count 1:  [ 2 ]
       count 2:  [ 1, 4 ]
     bucket 1 still has key 2, so min_freq stays 1

   now evict:  pop the FRONT of the min_freq (=1) bucket -> key 2
       count 1:  [ ]  -> delete empty bucket, min_freq rises to 2
```

- **Touch a key** (`get`, or `put` on an existing key): pull it from its count
  bucket, add one to its count, append it to the next count's bucket. If that
  emptied the `min_freq` bucket, `min_freq` rises by exactly one — the bucket the
  key just moved into.
- **Insert a new key**: it starts at count 1, so `min_freq` resets to 1.
- **Evict**: pop the *front* (oldest) key of the `min_freq` bucket. That key is the
  least frequent, and among those the least recent — both rules met, no scan.

Because `min_freq` only ever moves in single steps you can track directly, and every
bucket operation is a fixed cost, the whole cache stays fixed-cost.

## Complexity

- **Time: fixed cost** for both `get` and `put`. Finding the eviction victim is one
  step (front of the `min_freq` bucket); count bumps are fixed-cost ordered-dict
  moves.
- **Space: about `capacity`.** Three entries per key across the maps, plus the
  bucket structure.

## Pitfalls

- Getting `min_freq` maintenance wrong. It only changes in two places: set to 1 on
  any new insertion, and bumped by one when a touch empties the current min bucket.
  Rescanning for it defeats the purpose.
- Forgetting that **updating an existing key's value is a use** — it must bump the
  count, just like a `get`.
- Not deleting a bucket when it empties, leaving stale empty structures that confuse
  the `min_freq` logic.
- The `capacity == 0` case — the cache should store nothing and every `get` returns
  -1.
- Wrong tie-break: evicting the newest instead of the oldest within the min bucket.
  Pop the front, not the back.

## Transfer

LFU is [LRU Cache / 146](../0146-lru-cache/) with an extra frequency dimension — the
same "hash map for lookup + linked structure for ordered eviction" skeleton,
layered per count. The bucket-by-a-key idea also shows up in
[All O`one Data Structure / 432](https://leetcode.com/problems/all-oone-data-structure/),
where counts are bucketed to get fast min/max. When you need "fixed-cost access to
the extreme of a changing multiset," bucket by the key you rank on.
